"""Condition the forecasters' own Monte Carlo runs (unchanged model, unchanged priors)
on METR's Oct-2026 evidence, by importance weighting:

  posterior weight(sample) = 1[AC not reached by Oct 29 2026]
                             x  p_METR( model's 'acceleration due to AI' at Oct 2026 )

METR's 'acceleration due to AI' = current growth rate / counterfactual rate without AI.
Model analogue: progress_rates / human_only_progress_rates at T_NOW (same definition;
ECI is linear in progress in this model, so OOM rates and AECI-point rates scale alike).

The METR likelihood is built by Monte Carlo from what the report says:
  total acceleration ~ lognormal, 5-95% = [1.3, 3.0]  ("~2x; would not be surprised by 1.3x or 3x")
  AI share of it     ~ triangular(0.5, 0.8, 1.0)       ("a majority (perhaps ~80%) ... substantial uncertainty")
  AI-attributable    = total / (1 + (1-share)(total-1))
A second, stricter likelihood on the model's *total* acceleration (kink-fit slope ratio vs
METR's AECI 1.9x [1.5, 2.8]) is reported as a diagnostic.
"""
import glob, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "_ext" / "aifm-public" / "outputs" / "metr"
sys.path.insert(0, str(HERE))
from metr_obs import T_PRE0, T_BRK, T_NOW   # noqa: E402

AC_NOT_BEFORE = 2026.83
MILESTONES = ["AC", "AI2027-SC", "SAR-level-experiment-selection-skill", "TED-AI",
              "SIAR-level-experiment-selection-skill", "ASI"]
PARAMS = ["serial_uplift_at_reference_date", "excess_uplift_doubling_time", "inf_labor_asymptote",
          "ac_anchor_mode", "ai_research_taste_slope", "median_to_top_taste_multiplier",
          "inv_compute_anchor_exp_cap", "automation_logistic_asymptote", "parallel_penalty", "r_software"]


def metr_ai_accel_samples(n=400_000, seed=0):
    rng = np.random.default_rng(seed)
    mu, sig = np.log(np.sqrt(1.3 * 3.0)), np.log(3.0 / 1.3) / (2 * 1.645)
    total = np.exp(rng.normal(mu, sig, n))
    share = rng.triangular(0.5, 0.8, 1.0, n)
    return total / (1 + (1 - share) * (total - 1))


def log_density(samples, bw=0.05):
    """Gaussian KDE of log(samples) -> callable density over log(x)."""
    ls = np.log(samples); grid = np.linspace(ls.min() - 0.5, ls.max() + 0.5, 600)
    h, e = np.histogram(ls, bins=600, range=(grid[0], grid[-1]), density=True)
    c = 0.5 * (e[1:] + e[:-1]); k = np.exp(-0.5 * ((c[:, None] - c[None, :]) / bw) ** 2)
    dens = (k @ h) / k.sum(1)
    return lambda x: np.interp(np.log(np.clip(x, 1e-9, None)), c, dens, left=0, right=0)


def extract(run_dir, cache=True):
    """Pull per-sample observables + milestones + params out of rollouts.jsonl (cached)."""
    run_dir = Path(run_dir); cf = run_dir / "metr_extract.json"
    if cache and cf.exists() and cf.stat().st_mtime > (run_dir / "rollouts.jsonl").stat().st_mtime:
        return json.loads(cf.read_text())
    rows = []
    for line in open(run_dir / "rollouts.jsonl"):
        r = json.loads(line); res = r.get("results")
        if not res:
            rows.append(dict(ok=False)); continue
        t = np.asarray(res["times"], float); p = np.asarray(res["progress"], float)
        rate = np.asarray(res["progress_rates"], float); ho = np.asarray(res["human_only_progress_rates"], float)
        P = lambda x: float(np.interp(x, t, p))
        g = np.arange(T_PRE0, T_NOW + 1e-9, 1 / 12)
        X = np.c_[np.ones_like(g), g - T_BRK, np.clip(g - T_BRK, 0, None)]
        b = np.linalg.lstsq(X, np.interp(g, t, p), rcond=None)[0]
        rn, hn = float(np.interp(T_NOW, t, rate)), float(np.interp(T_NOW, t, ho))
        ms = res.get("milestones") or {}
        prm = {**r.get("parameters", {}), **(r.get("time_series_parameters") or {})}
        rows.append(dict(ok=True, ai_accel=rn / hn, kink=(b[1] + b[2]) / b[1], inst=rn / b[1],
                         ms={k: (ms.get(k) or {}).get("time") for k in MILESTONES},
                         params={k: prm.get(k) for k in PARAMS if k in prm} | {"r_software": res.get("r_software")}))
    cf.write_text(json.dumps(rows))
    return rows


def wquantile(x, w, qs):
    o = np.argsort(x); x, w = x[o], w[o]; c = np.cumsum(w) / w.sum()
    return [x[min(np.searchsorted(c, q), len(x) - 1)] for q in qs]


def summarize(rows, like_ai, like_kink):
    ok = [r for r in rows if r["ok"]]
    ai = np.array([r["ai_accel"] for r in ok]); kink = np.array([r["kink"] for r in ok])
    ac = np.array([r["ms"]["AC"] if r["ms"]["AC"] is not None else np.inf for r in ok])
    alive = (ac > AC_NOT_BEFORE).astype(float)
    W = {"prior": np.ones(len(ok)), "AC>Oct26": alive, "METR": alive * like_ai(ai),
         "METR+total": alive * like_ai(ai) * like_kink(kink)}
    out = dict(n_total=len(rows), n_ok=len(ok), ess={}, milestones={}, prob_by={}, params={}, obs={})
    for name, w in W.items():
        if w.sum() == 0:
            out["ess"][name] = 0; continue
        out["ess"][name] = float(w.sum() ** 2 / (w ** 2).sum())
        out["milestones"][name] = {}; out["prob_by"][name] = {}
        for m in MILESTONES:
            x = np.array([r["ms"][m] if r["ms"][m] is not None else np.inf for r in ok])
            out["milestones"][name][m] = [float(v) for v in wquantile(x, w, [0.1, 0.25, 0.5, 0.75, 0.9])]
            out["prob_by"][name][m] = {y: float((w * (x <= y)).sum() / w.sum()) for y in (2027, 2028, 2029, 2030, 2032, 2035, 2040)}
        out["obs"][name] = {"ai_accel": [float(v) for v in wquantile(ai, w, [0.1, 0.5, 0.9])],
                            "kink": [float(v) for v in wquantile(kink, w, [0.1, 0.5, 0.9])]}
        pp = {}
        for k in PARAMS:
            vals = [r["params"].get(k) for r in ok]
            if all(isinstance(v, str) for v in vals if v is not None) and any(isinstance(v, str) for v in vals):
                cats = sorted({v for v in vals if v is not None})
                pp[k] = {c: float(sum(wi for wi, v in zip(w, vals) if v == c) / w.sum()) for c in cats}
            else:
                arr = np.array([np.nan if v is None else float(v) for v in vals]); msk = np.isfinite(arr)
                if msk.sum():
                    pp[k] = [float(v) for v in wquantile(arr[msk], w[msk], [0.1, 0.5, 0.9])]
        out["params"][name] = pp
    out["_arrays"] = dict(ai=ai.tolist(), kink=kink.tolist(), w_metr=W["METR"].tolist(),
                          ms={m: [r["ms"][m] for r in ok] for m in MILESTONES},
                          params={k: [r["params"].get(k) for r in ok] for k in PARAMS})
    return out


def main():
    ai_s = metr_ai_accel_samples()
    like_ai = log_density(ai_s)
    mu, sig = np.log(1.9), (np.log(2.8) - np.log(1.5)) / (2 * 1.96)
    like_kink = lambda k: np.exp(-0.5 * ((np.log(np.clip(k, 1e-9, None)) - mu) / sig) ** 2)
    q = np.quantile(ai_s, [0.05, 0.5, 0.95])
    print(f"METR-implied AI-attributable acceleration: median {q[1]:.2f}, 90% [{q[0]:.2f}, {q[2]:.2f}]")
    res = {"metr_ai_accel_q": q.tolist(), "metr_ai_accel_samples": ai_s[:20000].tolist()}
    for fc in ("daniel", "eli", "brendan"):
        dirs = sorted(glob.glob(str(OUT / fc / "*")))
        if not dirs or not (Path(dirs[-1]) / "rollouts.jsonl").exists():
            continue
        s = summarize(extract(dirs[-1]), like_ai, like_kink)
        res[fc] = s
        print(f"\n== {fc}: {s['n_ok']}/{s['n_total']} ok; ESS " + ", ".join(f"{k}={v:.0f}" for k, v in s["ess"].items()))
        for name in ("prior", "METR"):
            if name not in s["milestones"]:
                continue
            o = s["obs"][name]
            print(f"  [{name:5s}] AI-accel p50={o['ai_accel'][1]:.2f} ({o['ai_accel'][0]:.2f}-{o['ai_accel'][2]:.2f}); kink p50={o['kink'][1]:.2f}")
            for m in ("AC", "SAR-level-experiment-selection-skill", "TED-AI", "ASI"):
                v = s["milestones"][name][m]; pb = s["prob_by"][name][m]
                print(f"     {m[:4]:4s} p10={v[0]:.1f} p50={v[2]:.1f} p90={v[4]:.1f} | P(<=2028)={pb[2028]:.2f} P(<=2030)={pb[2030]:.2f}")
    (HERE / "mc_conditioning.json").write_text(json.dumps(res, default=float))


if __name__ == "__main__":
    main()
