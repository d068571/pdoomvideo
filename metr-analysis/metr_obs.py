"""METR-comparable observables computed from an AI Futures Model run."""
import numpy as np

T_PRE0 = 2024.20   # Claude 3 Opus snapshot (start of METR's historical window, ~Mar 2024)
T_BRK = 2025.765   # METR's estimated AECI breakpoint, Oct 7 2025
T_NOW = 2026.75    # Model 4 snapshot / "as of October 2026"


def observables(m):
    R = m.results
    t = np.array(R['times']); p = np.array(R['progress'])
    r = np.array(R['progress_rates']); h = np.array(R['human_only_progress_rates'])
    P = lambda x: np.interp(x, t, p)
    hist = (P(T_BRK) - P(T_PRE0)) / (T_BRK - T_PRE0)
    # METR-style OLS fit with a single kink at Oct 7 2025 (monthly grid; ECI is linear in progress in this model)
    g = np.arange(T_PRE0, T_NOW + 1e-9, 1 / 12)
    X = np.c_[np.ones_like(g), g - T_BRK, np.clip(g - T_BRK, 0, None)]
    b = np.linalg.lstsq(X, P(g), rcond=None)[0]
    rn, hn = np.interp(T_NOW, t, r), np.interp(T_NOW, t, h)
    return dict(
        accel_kinkfit=(b[1] + b[2]) / b[1],          # like-for-like with METR's 1.9x
        accel_instant=rn / b[1],                     # current rate vs historical trend
        ai_accel_now=rn / hn,                        # METR's 'acceleration due to AI' (current / counterfactual)
        hist_rate_oom_yr=b[1], now_rate_oom_yr=rn, human_only_now=hn,
        train_growth_now=float(np.interp(T_NOW, t, R['training_system_performance_growth_rate'])),
    )
