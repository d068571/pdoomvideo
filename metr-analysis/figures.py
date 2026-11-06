"""Figures for the METR -> AI Futures Model analysis. Writes PNGs to ./figures/."""
import json, sys, warnings
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent / "_ext" / "aifm-public"
sys.path[:0] = [str(REPO), str(HERE)]
warnings.filterwarnings("ignore")
import metr_data as md   # noqa: E402

FIG = HERE / "figures"; FIG.mkdir(exist_ok=True)
# reference palette (light): categorical slots in fixed order + ink
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10.5, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlecolor": INK, "axes.titlelocation": "left", "legend.frameon": False, "lines.linewidth": 2,
    "legend.labelcolor": INK2,
})


def save(fig, name):
    fig.savefig(FIG / name, dpi=160, bbox_inches="tight"); plt.close(fig); print("wrote", name)


def model_runs():
    import playground.aifm as aifm
    sc = {s["name"].split(" ")[0]: s for s in json.load(open(HERE / "scenarios.json"))}
    out = {}
    for key in ("S0", "S1", "S2"):
        out[key] = (sc[key], aifm.model(**sc[key]["params"]))
    return sc, out


def fig_evidence():
    """AECI points + METR's kinked fit, and AECI vs Epoch ECI scale."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
    for name, (t, v, internal, frontier) in md.AECI_POINTS.items():
        col = C2 if internal else C1
        a.scatter(t, v, s=42 if frontier else 30, color=col if frontier else SURF, edgecolor=col, linewidth=1.6, zorder=3)
    for name in ("Claude 3 Opus", "Claude 3.7 Sonnet", "Claude Opus 4.5", "Mythos Preview", "Model 4"):
        t, v, *_ = md.AECI_POINTS[name]
        a.annotate(name, (t, v), xytext=(-6, 8), textcoords="offset points", ha="right", fontsize=8.5, color=INK2)
    B = md.BREAKPOINT
    pts = [(t, v) for t, v, i, f in md.AECI_POINTS.values() if f]
    t = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
    X = np.c_[np.ones_like(t), t - B, np.clip(t - B, 0, None)]; c = np.linalg.lstsq(X, y, rcond=None)[0]
    g1 = np.linspace(2024.1, B, 2); g2 = np.linspace(B, 2026.8, 2)
    a.plot(g1, c[0] + c[1] * (g1 - B), color=MUTED)
    a.plot(g2, c[0] + c[1] * (g2 - B), color=MUTED, ls="--", lw=1.4)
    a.plot(g2, c[0] + (c[1] + c[2]) * (g2 - B), color=INK)
    a.text(2024.6, 126, f"+{c[1]:.1f} pts/yr", color=INK2); a.text(2026.0, 176, f"+{c[1]+c[2]:.1f} pts/yr", color=INK, ha="right")
    a.axvline(B, color=GRID, lw=1, zorder=0)
    a.set_title(f"AECI read off METR's chart: kinked fit gives {(c[1]+c[2])/c[1]:.2f}x (METR: 1.9x)")
    a.set_ylabel("AECI (Anthropic's ECI)"); a.set_xlabel("date available to most Anthropic staff")
    a.scatter([], [], color=C1, label="public Anthropic model"); a.scatter([], [], color=C2, label="internal-only model")
    a.scatter([], [], color=SURF, edgecolor=MUTED, label="not frontier"); a.legend(loc="upper left")
    # scale conversion
    allp = {**{k: v[1] for k, v in md.AECI_POINTS.items()}, **md.AECI_OTHER}
    names = [k for k in md.EPOCH_ECI if k in allp]
    x = np.array([allp[k] for k in names]); yy = np.array([md.EPOCH_ECI[k] for k in names])
    anth = np.array([k in md.AECI_POINTS for k in names])
    b.plot([120, 182], [120, 182], color=GRID, lw=1.2, zorder=0); b.text(170, 173, "1:1", color=MUTED)
    b.scatter(x[anth], yy[anth], color=C1, s=34, label="Anthropic", zorder=3)
    b.scatter(x[~anth], yy[~anth], color=C3, s=34, label="other developers", zorder=3)
    a0, b0, _ = md.aeci_to_epoch_fit()
    late = ["Claude Opus 4.5", "Claude Opus 4.6", "Claude Opus 4.7", "Claude Opus 4.8", "Claude Opus 5",
            "Gemini 3 Pro", "GPT-5.2 Pro", "GPT-5 Pro"]
    a1, b1, _ = md.aeci_to_epoch_fit(late)
    xs = np.linspace(122, 180, 2)
    b.plot(xs, a0 + b0 * xs, color=INK2, lw=1.4, label=f"all models: slope {b0:.2f}")
    b.plot(xs, a1 + b1 * xs, color=INK, lw=2, label=f"post-Oct-2025 models: slope {b1:.2f}")
    b.scatter([md.MODEL4_AECI], [a1 + b1 * md.MODEL4_AECI], marker="x", color=C2, s=50, zorder=4)
    b.annotate("Model 4 (AECI 178.6)\n→ %.1f on Epoch scale" % (a1 + b1 * md.MODEL4_AECI), (md.MODEL4_AECI, a1 + b1 * md.MODEL4_AECI),
               xytext=(0, -42), textcoords="offset points", ha="right", fontsize=8.5, color=INK2)
    b.set_xlabel("AECI (METR chart)"); b.set_ylabel("Epoch ECI (the model's scale)")
    b.set_title("AECI points are worth ~0.64-0.81 Epoch points"); b.legend(loc="upper left", fontsize=9)
    save(fig, "f1_aeci_evidence.png")


def fig_accel(sc):
    rows = [("S0", "Website default (Daniel)"), ("S1-lo", "METR low end"), ("S1", "METR central"),
            ("S2", "METR + self-report growth"), ("S3", "Self-reports at face value"),
            ("S4", "METR + weak coding bottleneck")]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.0), sharey=True)
    lab = [r[1] for r in rows]; yy = np.arange(len(rows))[::-1]
    for ax, key, band, title in [
            (axes[0], "accel_kinkfit", (1.9, 1.5, 2.8), "Total acceleration vs Mar 2024–Oct 2025\n(METR's AECI measure, kinked fit)"),
            (axes[1], "ai_accel_now", (md.ai_attributable_accel(1.9), md.ai_attributable_accel(1.3), md.ai_attributable_accel(3.0)),
             "Acceleration due to AI, Oct 2026\n(rate with AI ÷ rate without AI)")]:
        ax.axvspan(band[1], band[2], color=C2, alpha=0.12, lw=0); ax.axvline(band[0], color=C2, lw=1.6)
        ax.text(band[0] + 0.03, -0.75, f"METR {band[0]:.2f}x (band: METR range)", color=INK2, fontsize=9)
        ax.set_ylim(-1.0, len(rows) - 0.5)
        vals = [sc[k][key] for k, _ in rows]
        ax.hlines(yy, 1, vals, color=GRID, lw=2)
        ax.scatter(vals, yy, color=C1, s=60, zorder=3)
        for v, y in zip(vals, yy):
            ax.text(v + 0.05, y + 0.22, f"{v:.2f}x", va="center", fontsize=9, color=INK)
        ax.axvline(1, color=MUTED, lw=1); ax.set_xlim(0.8, 3.0); ax.set_title(title); ax.grid(axis="y", visible=False)
        ax.set_xlabel("ratio of growth rates")
    axes[0].set_yticks(yy, lab)
    save(fig, "f2_acceleration_vs_metr.png")


def fig_rates(runs):
    import metr_obs as mo
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    for key, col, lab in (("S0", C1, "website default"), ("S1", C2, "METR-calibrated (S1)")):
        R = runs[key][1].results; t = np.array(R["times"]); m = (t > 2023.9) & (t < 2027.6)
        ax.plot(t[m], np.array(R["progress_rates"])[m], color=col, label=f"{lab}: with AI")
        ax.plot(t[m], np.array(R["human_only_progress_rates"])[m], color=col, ls="--", lw=1.5, label=f"{lab}: without AI (counterfactual)")
    hist = mo.observables(runs["S0"][1])["hist_rate_oom_yr"]
    ax.errorbar([mo.T_NOW], [hist * 1.9], yerr=[[hist * 0.4], [hist * 0.9]], fmt="D", color=INK, ms=7, capsize=4,
                label="METR: 1.9x [1.5–2.8] the historical rate", zorder=4)
    ax.hlines(hist, mo.T_PRE0, mo.T_BRK, color=INK, lw=1.2); ax.text(mo.T_BRK + 0.03, hist - 0.03, "historical average\n(website default)", color=INK2, fontsize=8.5, va="top")
    ax.axvline(mo.T_BRK, color=GRID, lw=1, zorder=0)
    ax.set_ylabel("growth of capability (OOMs of effective compute / yr)"); ax.set_ylim(0.9, 3.6)
    ax.set_title("Where the model and METR disagree: the model's capability growth barely rises by Oct 2026")
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    save(fig, "f3_progress_rates.png")


def fig_uplift(runs):
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    for key, col, lab in (("S0", C1, "S0 website default"), ("S1", C2, "S1 METR central"), ("S2", C3, "S2 + self-report growth")):
        R = runs[key][1].results; t = np.array(R["times"]); m = (t > 2024.9) & (t < 2027.3)
        ax.plot(t[m], np.array(R["serial_coding_labor_multipliers"])[m], color=col, label=f"model serial coding multiplier, {lab}")
    tt = np.array([p[0] for p in md.SELF_REPORTED_UPLIFT]); uu = np.array([p[1] for p in md.SELF_REPORTED_UPLIFT])
    ax.scatter(tt, uu, marker="^", s=60, color=INK, zorder=4, label="Anthropic staff self-reported uplift (METR chart)")
    td, lvl = md.self_report_excess_doubling_months(); g = np.linspace(2025.0, 2026.9, 50)
    ax.plot(g, lvl(g), color=INK, lw=1.2, ls=":", label=f"fit: excess uplift doubles every {td:.1f} months")
    ax.set_yscale("log"); ax.set_yticks([1, 2, 4, 8, 16, 32], ["1x", "2x", "4x", "8x", "16x", "32x"]); ax.set_ylim(0.9, 40)
    ax.set_title("AI uplift: staff self-reports vs. what the model needs to match METR")
    ax.legend(loc="upper left", fontsize=9); ax.set_ylabel("multiplier (log scale)")
    save(fig, "f4_uplift.png")


def fig_milestones(scl):
    rows = [s for s in scl if "milestones" in s]
    fig, ax = plt.subplots(figsize=(11, 0.55 * len(rows) + 1.4))
    yy = np.arange(len(rows))[::-1]
    for (m, col, mk, lab) in (("AC", C1, "o", "AC (automated coder)"),
                              ("SAR-level-experiment-selection-skill", C2, "s", "SAR (superhuman AI researcher)"),
                              ("ASI", C3, "D", "ASI")):
        xs = [r["milestones"][m] for r in rows]
        ax.scatter(xs, yy, color=col, marker=mk, s=55, zorder=3, label=lab, edgecolor=SURF, linewidth=1.5)
    for r, y in zip(rows, yy):
        ax.hlines(y, r["milestones"]["AC"], r["milestones"]["ASI"], color=GRID, lw=3, zorder=1)
        ax.text(r["milestones"]["ASI"] + 0.12, y, f"AC {r['milestones']['AC']:.1f} · ASI {r['milestones']['ASI']:.1f}", va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(yy, [r["name"] for r in rows]); ax.grid(axis="y", visible=False)
    ax.axvline(2026.83, color=MUTED, lw=1, ls="--"); ax.text(2026.88, yy[-1] - 0.45, "today", color=INK2, fontsize=8.5)
    ax.set_xlim(2026.5, 2039.5); ax.set_xlabel("year"); ax.legend(loc="upper right", fontsize=9)
    ax.set_title("Milestone dates under each METR-informed scenario (single trajectories)")
    save(fig, "f5_scenario_milestones.png")


if __name__ == "__main__":
    scl = json.load(open(HERE / "scenarios.json"))
    sc, runs = model_runs()
    fig_evidence(); fig_accel(sc); fig_rates(runs); fig_uplift(runs); fig_milestones(scl)
