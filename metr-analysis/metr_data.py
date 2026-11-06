"""Data extracted from METR, "Independent Assessment of AI R&D Acceleration at Anthropic
in October 2026" (2026-11-05), https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/

Stated numbers are quoted from the text. Per-model points were read off the published
charts (pixel measurement, ~±0.5 AECI pt / ±1 week / ±5% uplift); the report
does not publish the underlying tables.
"""
import numpy as np

# ---------------------------------------------------------------- headline findings (text)
ACCEL_AECI = dict(central=1.9, ci95=(1.5, 2.8))            # Anthropic AECI slope ratio, kink at Oct 7 2025
ACCEL_SUBJECTIVE = dict(central=2.0, plausible=(1.3, 3.0))  # METR staff's overall judgement, "as of Oct 2026"
ACCEL_ALL_DEVELOPERS = 1.4                                  # frontier incl. OpenAI/Google/xAI public models
AECI_SLOPE = dict(before=15.0, after=29.0)                  # AECI points / yr, Anthropic models
AECI_SLOPE_ALL_DEV = dict(before=17.0, after=24.0)          # AECI points / yr, all-developer frontier
BREAKPOINT = 2025.765                                       # Oct 7 2025 (estimated)
AI_SHARE_OF_ACCEL = 0.80                                    # "perhaps ~80%" of current acceleration due to AI
TRAINING_COMPUTE_ACCELERATED = False                        # "confident ... not due to an acceleration in training compute"
BOTTLENECKS_NEXT_12MO = "none significant found (algorithms, training compute, experiment compute, data); low confidence"
FULLY_AUTONOMOUS_CONTRIB = "not yet highly significant; 'signs of life' -> could occur soon"
HAIKU55_SYSTEM_CARD_ACCEL = 1.7
MODEL4_AECI = 178.6

ROBUSTNESS = {   # acceleration [95% CI] under alternative AECI analysis choices
    "link: logistic (main)": (1.9, 1.5, 2.8), "link: probit": (1.8, 1.3, 2.7),
    "link: cauchit": (2.8, 2.0, 4.1), "link: cloglog": (1.1, 0.8, 1.5),
    "link: loglog": (2.9, 2.1, 4.9), "link: learned Stukel": (2.6, 1.8, 4.1),
    "snapshots: highest per model": (1.9, 1.4, 2.8), "snapshots: first per model": (2.2, 1.3, 3.2),
    "snapshots: redacted subset": (1.9, 1.4, 3.3), "snapshots: all": (1.9, 1.4, 2.6),
    "bench: no vision": (2.2, 1.7, 3.5), "bench: AI-R&D relevant": (2.0, 1.5, 2.9),
    "bench: drop decreasing": (1.9, 1.6, 2.8), "bench: drop R2<50%": (1.9, 1.4, 2.6),
    "bench: stop at 85%": (1.9, 1.4, 2.3),
    "reg: 10x less L2": (1.9, 1.4, 2.8), "reg: 10x more L2": (2.1, 1.6, 3.0),
    "reg: none": (1.9, 1.4, 2.8), "reg: trend prior": (1.9, 1.4, 2.8),
}

INTERVIEWS_SUPPORT_2X = {"Yes": 2, "Leans yes": 3, "Borderline/unclear": 4, "Leans no": 0, "No": 2}
TOKENS_PER_TASK = dict(internal=(2.5e6, 72e3), agentic_coding=(10e6, 94e3))  # (input, output)

# ---------------------------------------------------------------- AECI by model (read off charts)
# (decimal date available to most Anthropic staff, AECI, internal?, frontier?)
AECI_POINTS = {
    "Claude 3 Opus": (2024.16, 124.7, False, True), "Claude 3.5 Sonnet": (2024.46, 130.0, False, True),
    "Claude 3.5 Sonnet New": (2024.77, 133.2, False, True), "Claude 3.7 Sonnet": (2025.13, 141.7, False, True),
    "Claude Opus 4": (2025.38, 144.8, False, True), "Claude Sonnet 4.5": (2025.73, 147.8, False, True),
    "Claude Opus 4.5": (2025.88, 152.6, False, True), "Claude Opus 4.6": (2026.07, 157.3, False, True),
    "Mythos Preview Early": (2026.15, 162.3, True, True), "Mythos Preview": (2026.25, 165.7, True, True),
    "Claude Opus 4.7": (2026.27, 160.3, False, False), "Claude Opus 4.8": (2026.40, 163.4, False, False),
    "Mythos 5": (2026.44, 168.6, False, True), "Model 2 Early": (2026.52, 171.9, True, True),
    "Claude Opus 5": (2026.54, 169.4, False, False), "Model 2": (2026.60, 174.1, True, True),
    "Mythos 5.1": (2026.60, 172.5, False, False), "Model 3 Early": (2026.69, 176.5, True, True),
    "Claude Opus 5.5": (2026.69, 174.7, False, False), "Model 3": (2026.73, 177.0, True, True),
    "Model 4": (2026.73, 178.6, True, True),
}
# Other developers' models on METR's all-developer AECI chart (AECI read off chart)
AECI_OTHER = {"o1-mini": 138.0, "o1": 143.9, "o3": 149.2, "Grok 4": 149.4, "GPT-5": 152.0,
              "GPT-5 Pro": 153.4, "Gemini 3 Pro": 154.7, "GPT-5.2 Pro": 158.4, "Gemini 3 Flash": 159.1}
# Epoch ECI for the same models (inputs/epoch/epoch_capabilities_index.csv, best variant)
EPOCH_ECI = {"Claude 3 Opus": 126.65, "Claude 3.5 Sonnet": 130.0, "Claude 3.5 Sonnet New": 134.23,
             "Claude 3.7 Sonnet": 141.61, "Claude Opus 4": 142.85, "Claude Sonnet 4.5": 146.83,
             "Claude Opus 4.5": 149.91, "Claude Opus 4.6": 155.15, "Claude Opus 4.7": 155.76,
             "Claude Opus 4.8": 157.88, "Claude Opus 5": 161.02,
             "o1-mini": 136.45, "o1": 142.45, "o3": 146.9, "Grok 4": 146.85, "GPT-5": 150.0,
             "GPT-5 Pro": 150.33, "Gemini 3 Pro": 153.2, "GPT-5.2 Pro": 155.03, "Gemini 3 Flash": 151.68}

# ---------------------------------------------------------------- self-reported uplift (chart)
# (date, uplift x, source). "Very loose evidence"; METR notes self-reports can overestimate.
SELF_REPORTED_UPLIFT = [
    (2025.13, 1.23, "Claude 3.7 Sonnet / targeted survey (hours saved)"),
    (2025.37, 1.34, "Claude Opus 4 / targeted survey (hours saved)"),
    (2025.89, 2.43, "Claude Opus 4.5 / targeted survey, adjusted to broad-poll scale"),
    (2026.10, 2.86, "Claude Opus 4.6 / broad Slack poll"),
    (2026.25, 3.96, "Mythos Preview / broad Slack poll"),
    (2026.41, 5.20, "Mythos 5 / broad Slack poll"),
    (2026.73, 12.0, "Model 4 / broad Slack poll"),
]
SELF_REPORTED_UPLIFT_UNADJUSTED = [(2025.89, 2.57, "Opus 4.5 % increase"), (2026.07, 2.17, "Opus 4.6 % increase")]
SELF_REPORT_EXP_FIT_PER_YEAR = 3.9


# ---------------------------------------------------------------- derived quantities
def ai_attributable_accel(total, share=AI_SHARE_OF_ACCEL):
    """METR's 'acceleration due to AI' = current / counterfactual-without-AI growth rate,
    when `share` of the excess growth over the historical rate is due to AI."""
    return total / (1 + (1 - share) * (total - 1))


def self_report_excess_doubling_months(points=SELF_REPORTED_UPLIFT):
    """OLS fit of log2(U-1) on time -> doubling time of the excess uplift (the model's
    `excess_uplift_doubling_time` definition), plus fitted level at a date."""
    t = np.array([p[0] for p in points]); y = np.log2(np.array([p[1] for p in points]) - 1)
    slope, icpt = np.polyfit(t, y, 1)
    return 12 / slope, (lambda d: 1 + 2 ** (icpt + slope * d))


def aeci_to_epoch_fit(names=None, since=None):
    """Linear map Epoch_ECI = a + b * AECI over models present in both datasets."""
    allp = {**{k: v[1] for k, v in AECI_POINTS.items()}, **AECI_OTHER}
    names = names or [k for k in EPOCH_ECI if k in allp]
    x = np.array([allp[k] for k in names]); y = np.array([EPOCH_ECI[k] for k in names])
    b, a = np.polyfit(x, y, 1)
    return a, b, names


if __name__ == "__main__":
    for tot in (ACCEL_AECI["central"], *ACCEL_SUBJECTIVE["plausible"], *ACCEL_AECI["ci95"]):
        print(f"total accel {tot}: AI-attributable {ai_attributable_accel(tot):.2f}")
    td, lvl = self_report_excess_doubling_months()
    print(f"self-report excess-uplift doubling time: {td:.2f} months; fitted level Aug 2026 {lvl(2026.578):.1f}x, Oct 2026 {lvl(2026.75):.1f}x")
    td2, lvl2 = self_report_excess_doubling_months(SELF_REPORTED_UPLIFT[2:])
    print(f"  (slack-poll era only, Nov 2025+): {td2:.2f} months; Aug 2026 level {lvl2(2026.578):.1f}x")
    a, b, n = aeci_to_epoch_fit(); print(f"Epoch = {a:.1f} + {b:.3f} AECI  (all {len(n)} matched models)")
    late = [k for k in EPOCH_ECI if k in ("Claude Opus 4.5", "Claude Opus 4.6", "Claude Opus 4.7", "Claude Opus 4.8",
                                         "Claude Opus 5", "Gemini 3 Pro", "GPT-5.2 Pro", "GPT-5 Pro")]
    a2, b2, _ = aeci_to_epoch_fit(late); print(f"Epoch = {a2:.1f} + {b2:.3f} AECI  (post-Oct-2025 models)")
    for lab, bb in (("all", b), ("recent", b2)):
        print(f"  [{lab}] Anthropic AECI slopes 15 -> 29 /yr  ==  Epoch-scale {15*bb:.1f} -> {29*bb:.1f} /yr")
