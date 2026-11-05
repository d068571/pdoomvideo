"""Playground helpers for the AI Futures Model (aifuturesmodel.com).

`run()` goes through the website's own Flask handler (`api/index.py`,
POST /api/compute) in-process, so a result is exactly what the website would
compute and chart for the same parameters. `model()` gives you the raw
`ProgressModel` object for digging into internals.

Parameters here are in **API units** (what the browser actually POSTs):
  * ac_time_horizon_minutes  -> minutes (the website UI stores log10(minutes))
  * parallel_penalty         -> the UI's coding_labor_exponent
  * include_gap              -> 'gap' / 'no gap' (UI: benchmarks_and_gaps_mode)
Presets from the website are converted for you with the same rules as
`convertParametersToAPIFormat` in utils/monteCarlo.ts.

Quick start (from the repo root, venv active):
    import playground.aifm as aifm
    r = aifm.run()                       # homepage forecast (Daniel, 08/16/26)
    r.milestones                         # milestone dates
    aifm.sweep('excess_uplift_doubling_time', [3, 5, 8, 12])
"""
from __future__ import annotations

import contextlib
import io
import json
import logging
import math
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

def _quiet():
    """The model sets its loggers to INFO on import; turn them down."""
    logging.getLogger().setLevel(logging.WARNING)
    for name in list(logging.root.manager.loggerDict):
        if name.split(".")[0] in ("progress_model", "api", "werkzeug"):
            logging.getLogger(name).setLevel(logging.WARNING)

import pandas as pd  # noqa: E402

PRESETS_FILE = Path(__file__).with_name("presets.json")
DEFAULT_TIME_RANGE = (2017, 2200)  # what the website's homepage requests
TIME_SERIES_KEYS = (
    "constant_training_system_performance_growth_rate",
    "slowdown_year",
    "post_slowdown_training_system_performance_growth_rate",
)
HEADLINE = ["AC", "AI2027-SC", "SAR-level-experiment-selection-skill", "TED-AI",
            "SIAR-level-experiment-selection-skill", "ASI"]


# --------------------------------------------------------------------------- presets
def _load_presets() -> dict:
    if not PRESETS_FILE.exists():
        raise FileNotFoundError(
            f"{PRESETS_FILE} missing; regenerate with: npx tsx playground/export_presets.ts")
    return json.loads(PRESETS_FILE.read_text())


_PRESETS = _load_presets()
DEFAULT_PRESET = _PRESETS["default"]


def list_presets() -> pd.DataFrame:
    """The presets in the website's dropdown (plus aliases in `all_presets()`)."""
    return pd.DataFrame(_PRESETS["menu"])


def all_presets() -> list[str]:
    return list(_PRESETS["presets"])


def to_api_format(ui_params: dict) -> dict:
    """Port of utils/monteCarlo.ts::convertParametersToAPIFormat."""
    p = dict(ui_params)
    if isinstance(p.get("ac_time_horizon_minutes"), (int, float)):
        p["ac_time_horizon_minutes"] = 10 ** p["ac_time_horizon_minutes"]
    if p.get("serial_uplift_at_reference_date") is not None and "swe_multiplier_at_present_day" in p:
        del p["swe_multiplier_at_present_day"]
    if "benchmarks_and_gaps_mode" in p:
        v = p.pop("benchmarks_and_gaps_mode")
        p["include_gap"] = "gap" if v in (True, "gap") else "no gap"
    if isinstance(p.get("coding_labor_exponent"), (int, float)):
        p["parallel_penalty"] = p.pop("coding_labor_exponent")
    return p


def params(preset: str | None = DEFAULT_PRESET, **overrides) -> dict:
    """API-format parameter dict: a website preset (or {} for the Python
    defaults when preset=None) with `overrides` (API units) applied on top."""
    base = {} if preset is None else to_api_format(_PRESETS["presets"][preset])
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- running
_client = None


def _api():
    global _client
    if _client is None:
        from api.index import app
        app.logger.setLevel(logging.WARNING)
        _client = app.test_client()
        _quiet()
    return _client


def decimal_year_to_str(y) -> str:
    if y is None or (isinstance(y, float) and not math.isfinite(y)):
        return "not reached"
    year = int(math.floor(y))
    month = int((y - year) * 12) + 1
    return f"{year}-{month:02d}"


@dataclass
class Run:
    params: dict
    raw: dict = field(repr=False)
    label: str = ""

    @property
    def milestones(self) -> pd.DataFrame:
        rows = []
        for name, m in self.raw["milestones"].items():
            t = m.get("time")
            rows.append({"milestone": name, "year": t, "date": decimal_year_to_str(t),
                         "effective_compute_ooms": m.get("effective_compute_ooms"),
                         "progress_multiplier": m.get("progress_multiplier")})
        return pd.DataFrame(rows).set_index("milestone")

    @property
    def series(self) -> pd.DataFrame:
        """Per-timestep trajectory (same columns the website charts use)."""
        df = pd.DataFrame(self.raw["time_series"]).set_index("year")
        return df.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")

    @property
    def summary(self) -> dict:
        return self.raw["summary"]

    def date(self, milestone: str) -> str:
        return decimal_year_to_str(self.raw["milestones"].get(milestone, {}).get("time"))

    @property
    def ac(self):
        return self.raw["milestones"]["AC"]["time"]

    @property
    def asi(self):
        return self.raw["milestones"]["ASI"]["time"]

    def __repr__(self):
        heads = ", ".join(f"{m.split('-')[0]}={self.date(m)}" for m in HEADLINE if m in self.raw["milestones"])
        return f"Run({self.label or 'custom'}: {heads})"


def run(preset: str | None = DEFAULT_PRESET, *, time_range=DEFAULT_TIME_RANGE,
        label: str = "", custom_time_series: dict | None = None, **overrides) -> Run:
    """Compute one trajectory exactly as the website does.

    run()                                    -> homepage forecast
    run('eli-08-16-26')                      -> another forecaster's median
    run(ac_anchor_mode='time-horizon', ac_time_horizon_minutes=1e6)
    run(None)                                -> bare Python defaults (no preset)
    NOTE: the compute-growth knobs (constant_training_system_performance_growth_rate,
    slowdown_year, post_slowdown_...) are accepted but have NO effect: upstream
    progress_model/time_series.py returns the base CSV ("TEMPORARILY DISABLED"),
    on the live site too. For compute scenarios pass custom_time_series, e.g.
    run(custom_time_series=compute_scenario(after=2027, growth_multiplier=0.5)).
    """
    p = params(preset, **overrides)
    body = {"parameters": p, "time_range": list(time_range), "initial_progress": 0,
            "use_exponential_growth_inputs": False}
    if custom_time_series is not None:
        body["custom_time_series"] = custom_time_series
    with contextlib.redirect_stdout(io.StringIO()):  # the API prints debug lines
        resp = _api().post("/api/compute", json=body)
    data = resp.get_json()
    if resp.status_code != 200 or not data.get("success", False):
        raise RuntimeError(f"model failed ({resp.status_code}): {data.get('error', data)}")
    return Run(params=p, raw=data, label=label or (preset or "python-defaults"))


def default_time_series() -> pd.DataFrame:
    """The input series (labor, compute) the site uses; editable copy for
    run(custom_time_series=df_to_custom(df))."""
    resp = _api().get("/api/default-data")
    return pd.DataFrame(resp.get_json()["time_series"])


def df_to_custom(df: pd.DataFrame) -> dict:
    return {c: df[c].astype(float).tolist() for c in df.columns}


COMPUTE_COLUMNS = ("training_H100e", "experiment_H100e", "inference_H100e")


def compute_scenario(after: float = 2027.0, growth_multiplier: float = 0.0,
                     columns=COMPUTE_COLUMNS, ts: pd.DataFrame | None = None) -> dict:
    """Input series with growth (in log space) of `columns` scaled after `after`:
    growth_multiplier 0 freezes them, 0.5 halves the OOMs/yr, 2 doubles them.
    Add 'L_HUMAN' to columns to also change human labor growth.
    Returns a dict for run(custom_time_series=...)."""
    import numpy as np
    df = (ts if ts is not None else default_time_series()).copy()
    late = df["time"] > after
    for c in columns:
        v0 = np.exp(np.interp(after, df["time"], np.log(df[c])))
        df.loc[late, c] = v0 * (df.loc[late, c] / v0) ** growth_multiplier
    return df_to_custom(df)


def sweep(param: str, values, preset: str | None = DEFAULT_PRESET,
          milestones=("AC", "SAR-level-experiment-selection-skill", "ASI"), **overrides) -> pd.DataFrame:
    """Milestone years as one parameter varies (other params fixed)."""
    rows = []
    for v in values:
        try:
            r = run(preset, **{**overrides, param: v})
            rows.append({param: v, **{m: r.raw["milestones"].get(m, {}).get("time") for m in milestones}})
        except Exception as e:  # keep sweeping past infeasible points
            rows.append({param: v, "error": str(e)[:120]})
    return pd.DataFrame(rows).set_index(param)


def compare(*runs: Run, milestones=HEADLINE) -> pd.DataFrame:
    return pd.DataFrame({r.label or f"run{i}": {m: r.date(m) for m in milestones}
                         for i, r in enumerate(runs)})


def plot(*runs: Run, column: str = "progress", logy: bool = False, xlim=(2022, 2040), ax=None):
    """Overlay one series column (see Run.series.columns) for several runs."""
    import matplotlib.pyplot as plt
    ax = ax or plt.subplots(figsize=(9, 5))[1]
    for r in runs:
        s = r.series[column]
        if logy:
            s = s.where(s > 0)
        ax.plot(s.index, s.values, label=r.label)
        if "AC" in r.raw["milestones"] and r.ac:
            ax.axvline(r.ac, ls=":", lw=0.8, color=ax.lines[-1].get_color())
    if logy:
        ax.set_yscale("log")
    ax.set_xlim(*xlim)
    ax.set_xlabel("year"); ax.set_ylabel(column); ax.legend(); ax.grid(alpha=0.3)
    return ax


# --------------------------------------------------------------------------- internals
def model(preset: str | None = DEFAULT_PRESET, *, time_range=DEFAULT_TIME_RANGE, **overrides):
    """Build and run a raw ProgressModel with the same inputs the API would use.
    Returns the model; see model.results, model.human_only_results, etc."""
    from api.index import drop_unknown_params, create_default_time_series
    from progress_model import Parameters, ProgressModel
    from progress_model.time_series import generate_time_series_from_dict
    _quiet()
    p = params(preset, **overrides)
    ts_params = {k: p[k] for k in TIME_SERIES_KEYS if k in p}
    mp = {k: v for k, v in p.items() if k not in TIME_SERIES_KEYS}
    if len(ts_params) == 3:
        ts = generate_time_series_from_dict(ts_params, str(REPO / "inputs" / "input_data.csv"))
    else:
        ts = create_default_time_series()
    m = ProgressModel(Parameters(**drop_unknown_params(mp)), ts)
    m.compute_progress_trajectory(list(time_range), 0)
    return m


# --------------------------------------------------------------------------- Monte Carlo
def list_sampling_configs() -> list[str]:
    """Forecaster uncertainty configs (Q2 = the ones behind the current /forecast page)."""
    return sorted(str(p.relative_to(REPO)) for p in (REPO / "config").glob("sampling_config*.yaml"))


def monte_carlo(config: str = "config/sampling_config_q2_daniel.yaml", num_samples: int = 200,
                num_workers: int = 4, seed: int = 42, output_dir: str = "outputs/playground",
                extra_args: tuple = ()) -> Path:
    """Run scripts/pipelines/batch_rollout.py (the pipeline behind /forecast) and
    return the run directory. ~1-2 s per sample per worker. Uses the 'spawn'
    multiprocessing context: the default 'fork' crashes on Python 3.14."""
    import subprocess
    out = REPO / output_dir
    before = set(out.glob("*")) if out.exists() else set()
    cmd = [sys.executable, "scripts/pipelines/batch_rollout.py", "--config", config,
           "--num-samples", str(num_samples), "--num-workers", str(num_workers),
           "--seed", str(seed), "--mp-context", "spawn", "--output-dir", str(out), *extra_args]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    new = sorted(set(out.glob("*")) - before)
    if proc.returncode != 0 or not new:
        raise RuntimeError(proc.stderr[-3000:])
    return new[-1]


def load_rollouts(run_dir) -> pd.DataFrame:
    """One row per sample: milestone years (NaN = not reached), plus 'error'."""
    rows = []
    for line in open(Path(run_dir) / "rollouts.jsonl"):
        r = json.loads(line)
        res = r.get("results") or {}
        row = {"sample_id": r.get("sample_id"), "error": r.get("error")}
        for name, m in (res.get("milestones") or {}).items():
            t = m.get("time") if isinstance(m, dict) else None
            row[name] = float("nan") if t is None else t
        rows.append(row)
    return pd.DataFrame(rows).set_index("sample_id")


def mc_summary(run_dir, milestones=HEADLINE, by_years=(2027, 2028, 2030, 2035, 2050)) -> pd.DataFrame:
    """Percentiles of milestone dates and P(reached by year) over successful samples.
    Unreached milestones count as 'later than everything' (as the site does)."""
    df = load_rollouts(run_dir)
    ok = df[df["error"].isna()]
    out = {}
    for m in milestones:
        if m not in ok:
            continue
        x = ok[m].fillna(float("inf"))
        row = {f"p{q}": x.quantile(q / 100, interpolation="lower") for q in (10, 25, 50, 75, 90)}
        row.update({f"P(by {y})": float((x <= y).mean()) for y in by_years})
        out[m] = row
    res = pd.DataFrame(out).T
    res.attrs["n_ok"], res.attrs["n_failed"] = len(ok), len(df) - len(ok)
    return res


if __name__ == "__main__":
    r = run()
    print(r)
    print(r.milestones[["date", "year"]].to_string())
