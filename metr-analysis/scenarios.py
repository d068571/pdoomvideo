"""Deterministic METR-informed scenarios on top of the website default (Daniel, 08/16/26).
No model code is changed: only parameter values (and AC-anchor inputs) are set.
Run from anywhere:  ../_ext/aifm-public/.venv/bin/python scenarios.py
"""
import json, math, sys, warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent / "_ext" / "aifm-public"
sys.path[:0] = [str(REPO), str(HERE)]
warnings.filterwarnings("ignore")

import playground.aifm as aifm          # noqa: E402
import metr_obs as mo                   # noqa: E402
import metr_data as md                  # noqa: E402

AC_NOT_BEFORE = 2026.83                 # METR: no fully autonomous significant contributions as of Oct 29 2026
TARGET = md.ai_attributable_accel(md.ACCEL_AECI["central"])            # 1.61
TARGET_LO = md.ai_attributable_accel(md.ACCEL_SUBJECTIVE["plausible"][0])  # 1.23
TARGET_HI = md.ai_attributable_accel(md.ACCEL_SUBJECTIVE["plausible"][1])  # 2.14
TD_SELF, LEVEL_SELF = md.self_report_excess_doubling_months()          # 3.47 mo, level(t)
A_RECENT, B_RECENT, _ = md.aeci_to_epoch_fit(["Claude Opus 4.5", "Claude Opus 4.6", "Claude Opus 4.7",
                                              "Claude Opus 4.8", "Claude Opus 5", "Gemini 3 Pro", "GPT-5.2 Pro", "GPT-5 Pro"])
ECI_NOW_EPOCH = A_RECENT + B_RECENT * md.MODEL4_AECI                   # Model 4 on Epoch scale
ECI_RATE_EPOCH = B_RECENT * md.AECI_SLOPE["after"]                     # 29 AECI/yr on Epoch scale


def evaluate(over):
    m = aifm.model(**over)
    o = mo.observables(m)
    o["AC"] = m.results["aa_time"]
    o["milestones"] = {k: v.get("time") for k, v in m.results["milestones"].items()}
    return o


def solve_uplift(target, base, lo=1.05, hi=40.0, iters=18):
    """Bisect serial_uplift_at_reference_date so that METR's 'acceleration due to AI'
    (model: progress rate / human-only progress rate at Oct 2026) equals `target`."""
    def f(S):
        try:
            return evaluate({**base, "serial_uplift_at_reference_date": S})["ai_accel_now"] - target
        except Exception:
            return None
    while f(hi) is None and hi > lo * 1.1:
        hi /= 1.3
    fh = f(hi)
    if fh is None or fh < 0:
        return None, hi
    for _ in range(iters):
        mid = math.sqrt(lo * hi)
        fm = f(mid)
        if fm is None or fm > 0:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi), None


def main():
    base_daniel = {}
    specs = [
        ("S0 Website default (Daniel 08/16/26)", {}, None),
        ("S1 METR-calibrated uplift (Daniel's other beliefs)", {}, TARGET),
        ("S1-lo METR low end (1.3x total)", {}, TARGET_LO),
        ("S1-hi METR high end (3x total)", {}, TARGET_HI),
        ("S2 METR-calibrated + self-reported uplift growth", {"excess_uplift_doubling_time": TD_SELF}, TARGET),
        ("S3 Self-reports at face value", {"excess_uplift_doubling_time": TD_SELF,
                                           "serial_uplift_at_reference_date": LEVEL_SELF(2026.578082)}, None),
        ("S4 METR-calibrated + weak coding bottleneck", {"inf_labor_asymptote": 200.0}, TARGET),
        ("S5 METR-calibrated, AC anchored on METR's AECI", {"ac_anchor_mode": "eci", "eci_at_present_day": ECI_NOW_EPOCH,
                                                             "eci_reference_date": 2026.73, "eci_growth_rate": ECI_RATE_EPOCH}, TARGET),
        ("S6-base AC anchored on ECI, Daniel's own ECI beliefs", {"ac_anchor_mode": "eci"}, None),
        ("S6 AC anchored on METR's AECI only (no uplift change)", {"ac_anchor_mode": "eci", "eci_at_present_day": ECI_NOW_EPOCH,
                                                                  "eci_reference_date": 2026.73, "eci_growth_rate": ECI_RATE_EPOCH}, None),
    ]
    out = []
    for name, over, target in specs:
        over = dict(over)
        note = ""
        if target is not None:
            S, cap = solve_uplift(target, over)
            if S is None:
                note = f"target {target:.2f} unreachable (max feasible S≈{cap:.1f})"
                print(name, note); out.append(dict(name=name, params=over, note=note)); continue
            over["serial_uplift_at_reference_date"] = S
        o = evaluate(over)
        if o["AC"] is not None and o["AC"] < AC_NOT_BEFORE:
            note = "AC before Oct 29 2026: inconsistent with METR"
        rec = dict(name=name, params=over, target=target, note=note, **o)
        out.append(rec)
        ms = o["milestones"]
        print(f"{name}\n   params={ {k: round(v, 3) if isinstance(v, float) else v for k, v in over.items()} }"
              f"\n   AI-accel={o['ai_accel_now']:.2f} kink={o['accel_kinkfit']:.2f} inst={o['accel_instant']:.2f}"
              f" | AC={aifm.decimal_year_to_str(ms['AC'])} SAR={aifm.decimal_year_to_str(ms['SAR-level-experiment-selection-skill'])}"
              f" TED-AI={aifm.decimal_year_to_str(ms['TED-AI'])} ASI={aifm.decimal_year_to_str(ms['ASI'])} {note}")
    json.dump(out, open(HERE / "scenarios.json", "w"), indent=1, default=float)
    print(f"\nconstants: target={TARGET:.3f} [{TARGET_LO:.3f}, {TARGET_HI:.3f}], Td_self={TD_SELF:.2f} mo, "
          f"self level Aug26={LEVEL_SELF(2026.578082):.2f}, ECI now={ECI_NOW_EPOCH:.1f} rate={ECI_RATE_EPOCH:.1f}")


if __name__ == "__main__":
    main()
