"""Figures for the METR-conditioned Monte Carlo (reads mc_conditioning.json)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figures as F   # shared style

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "mc_conditioning.json").read_text())
FCS = [f for f in ("daniel", "eli", "brendan") if f in D]
NAMES = {"daniel": "Daniel", "eli": "Eli", "brendan": "Brendan"}


def wcdf(x, w, grid):
    x = np.array([np.inf if v is None else v for v in x], float); w = np.asarray(w, float)
    return np.array([(w * (x <= g)).sum() / w.sum() for g in grid])


def fig_cdfs():
    grid = np.linspace(2026.5, 2040, 400)
    fig, axes = plt.subplots(2, len(FCS), figsize=(4.4 * len(FCS), 7.2), sharex=True, sharey=True)
    axes = np.atleast_2d(axes)
    for j, fc in enumerate(FCS):
        A = D[fc]["_arrays"]; n = len(A["ai"]); wp = np.ones(n); wm = np.array(A["w_metr"])
        for i, (m, lab) in enumerate((("AC", "Automated coder (AC)"), ("ASI", "ASI"))):
            ax = axes[i, j]
            ax.plot(grid, wcdf(A["ms"][m], wp, grid), color=F.C1, label="forecaster's prior")
            ax.plot(grid, wcdf(A["ms"][m], wm, grid), color=F.C2, label="conditioned on METR")
            ax.axvline(2026.83, color=F.MUTED, lw=1, ls="--")
            ax.set_title(f"{NAMES[fc]} — {lab}", fontsize=11)
            if j == 0: ax.set_ylabel("P(milestone reached by year)")
            if i == 1: ax.set_xlabel("year")
            ess = D[fc]["ess"]["METR"]
            ax.text(0.98, 0.04, f"ESS {ess:.0f} / {n}", transform=ax.transAxes, ha="right", color=F.INK2, fontsize=8.5)
    axes[0, 0].legend(loc="lower right", fontsize=9, bbox_to_anchor=(1.0, 0.1))
    fig.suptitle("Monte Carlo milestone CDFs: forecasters' own uncertainty, before vs after METR's evidence",
                 x=0.01, ha="left", fontweight="bold", color=F.INK)
    fig.tight_layout(); F.save(fig, "m1_mc_cdfs.png")


def fig_ai_accel():
    metr = np.array(D["metr_ai_accel_samples"])
    bins = np.exp(np.linspace(np.log(0.9), np.log(3.2), 46))
    fig, axes = plt.subplots(1, len(FCS), figsize=(4.4 * len(FCS), 3.8), sharey=True)
    for ax, fc in zip(np.atleast_1d(axes), FCS):
        A = D[fc]["_arrays"]; ai = np.array(A["ai"]); wm = np.array(A["w_metr"])
        ax.hist(ai, bins=bins, density=True, color=F.C1, alpha=0.35, label="model, prior samples")
        ax.hist(ai, bins=bins, weights=wm, density=True, histtype="step", color=F.C2, lw=2, label="model, conditioned")
        ax.hist(metr, bins=bins, density=True, histtype="step", color=F.INK, lw=1.4, ls="--", label="METR evidence")
        ax.set_xscale("log"); ax.set_xticks([1, 1.25, 1.5, 2, 2.5, 3], ["1", "1.25", "1.5", "2", "2.5", "3"])
        ax.set_title(f"{NAMES[fc]}", fontsize=11); ax.set_xlabel("acceleration due to AI, Oct 2026")
    np.atleast_1d(axes)[0].legend(fontsize=8.5, loc="upper right"); np.atleast_1d(axes)[0].set_ylabel("density")
    fig.suptitle("The forecasters' priors put most weight below METR's estimate of AI-driven acceleration",
                 x=0.01, ha="left", fontweight="bold", color=F.INK)
    fig.tight_layout(); F.save(fig, "m2_ai_accel.png")


if __name__ == "__main__":
    fig_cdfs(); fig_ai_accel()
