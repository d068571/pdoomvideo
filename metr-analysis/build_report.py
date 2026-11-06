"""Assemble report.html (self-contained: figures embedded) from scenarios.json + mc_conditioning.json."""
import base64, html, json
from pathlib import Path
import metr_data as md

HERE = Path(__file__).resolve().parent
SC = json.loads((HERE / "scenarios.json").read_text())
MC = json.loads((HERE / "mc_conditioning.json").read_text())
FCS = [f for f in ("daniel", "eli", "brendan") if f in MC]
NAMES = {"daniel": "Daniel", "eli": "Eli", "brendan": "Brendan"}


def img(name, alt):
    b = base64.b64encode((HERE / "figures" / name).read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" alt="{html.escape(alt)}"></figure>'


def ym(y):
    if y is None or y == float("inf") or (isinstance(y, float) and y != y) or y > 2199:
        return "not reached"
    yr = int(y); mo = int((y - yr) * 12) + 1
    return f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][mo-1]} {yr}"


def table(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def scen_rows():
    out = []
    for s in SC:
        if "milestones" not in s:
            out.append([html.escape(s["name"]), "—", "—", "—", "—", "—", "—", html.escape(s.get("note", ""))]); continue
        p = s["params"]; m = s["milestones"]
        ptxt = ", ".join(f"{k}={v:.3g}" if isinstance(v, (int, float)) else f"{k}={v}" for k, v in p.items()) or "(none)"
        out.append([html.escape(s["name"]), f"<code>{html.escape(ptxt)}</code>", f"{s['accel_kinkfit']:.2f}x",
                    f"{s['ai_accel_now']:.2f}x", ym(m["AC"]), ym(m["SAR-level-experiment-selection-skill"]),
                    ym(m["ASI"]), html.escape(s.get("note", ""))])
    return out


def mc_rows():
    rows = []
    for fc in FCS:
        d = MC[fc]
        for w, lab in (("prior", "prior (forecaster's own)"), ("AC>Oct26", "+ 'no AC yet'"), ("METR", "+ METR AI acceleration")):
            if w not in d["milestones"]:
                continue
            ms, pb = d["milestones"][w], d["prob_by"][w]
            rows.append([NAMES[fc] if w == "prior" else "", lab, f"{d['ess'][w]:.0f}",
                         f"{d['obs'][w]['ai_accel'][1]:.2f}x",
                         f"{ym(ms['AC'][2])} <span class='mut'>({ym(ms['AC'][0])} – {ym(ms['AC'][4])})</span>",
                         f"{pb['AC']['2028']:.0%}",
                         f"{ym(ms['ASI'][2])} <span class='mut'>({ym(ms['ASI'][0])} – {ym(ms['ASI'][4])})</span>",
                         f"{pb['ASI']['2030']:.0%}"])
    return rows


def param_rows():
    rows = []
    for fc in FCS:
        P = MC[fc]["params"]
        for k, lab in (("serial_uplift_at_reference_date", "Serial coding uplift, Aug 2026"),
                       ("excess_uplift_doubling_time", "Excess-uplift doubling time (months)"),
                       ("inf_labor_asymptote", "Speedup cap from unlimited coding labor"),
                       ("ai_research_taste_slope", "AI research-taste slope")):
            if k in P["prior"]:
                a, b = P["prior"][k], P["METR"][k]
                rows.append([NAMES[fc], lab, f"{a[1]:.3g} <span class='mut'>({a[0]:.3g}–{a[2]:.3g})</span>",
                             f"{b[1]:.3g} <span class='mut'>({b[0]:.3g}–{b[2]:.3g})</span>"])
        if "ac_anchor_mode" in P["prior"]:
            a, b = P["prior"]["ac_anchor_mode"], P["METR"]["ac_anchor_mode"]
            rows.append([NAMES[fc], "AC anchor-mode mix", ", ".join(f"{k} {v:.0%}" for k, v in a.items()),
                         ", ".join(f"{k} {v:.0%}" for k, v in b.items())])
    return rows


def build(narrative):
    css = """
:root{--bg:#fcfcfb;--fg:#0b0b0b;--fg2:#52514e;--mut:#8a8984;--line:#e6e5e1;--card:#f4f3f0;--acc:#2a78d6;--acc2:#eb6834}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1a1a19;--fg:#f0efec;--fg2:#c3c2b7;--mut:#9a998f;--line:#34332f;--card:#24241f;--acc:#3987e5;--acc2:#d95926}}
:root[data-theme="dark"]{--bg:#1a1a19;--fg:#f0efec;--fg2:#c3c2b7;--mut:#9a998f;--line:#34332f;--card:#24241f;--acc:#3987e5;--acc2:#d95926}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Inter,system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1040px;margin:0 auto;padding:32px 16px 80px}h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:21px;margin:44px 0 10px;padding-top:12px;border-top:1px solid var(--line)}h3{font-size:17px;margin:26px 0 6px}
p,li{color:var(--fg)}.sub{color:var(--fg2);margin:0 0 22px}.mut{color:var(--mut);font-size:.88em}
figure{margin:18px 0;background:#fcfcfb;border-radius:10px;padding:8px;border:1px solid var(--line)}figure img{width:100%;height:auto;display:block}
.tw{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--fg2);font-weight:600;background:var(--card)}code{font-size:12.5px;word-break:break-word}
.key{background:var(--card);border-left:4px solid var(--acc2);padding:14px 18px;border-radius:8px;margin:18px 0}
.key li{margin:6px 0}.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:18px 0}
.tile{background:var(--card);border-radius:10px;padding:14px}.tile b{display:block;font-size:24px;line-height:1.2}.tile span{color:var(--fg2);font-size:13.5px}
"""
    import re
    body = narrative
    body = re.sub(r"\[\[IMG:([^|\]]+)\|([^\]]+)\]\]", lambda m: img(m.group(1), m.group(2)), body)
    body = body.replace("[[SCEN_TABLE]]", table(
        ["Scenario", "Parameters changed (vs website default)", "Total accel.", "AI accel.", "AC", "SAR", "ASI", "Note"], scen_rows()))
    body = body.replace("[[MC_TABLE]]", table(["Forecaster", "Conditioning", "ESS", "AI accel. p50", "AC median (p10–p90)",
                                               "P(AC≤2028)", "ASI median (p10–p90)", "P(ASI≤2030)"], mc_rows()))
    body = body.replace("[[PARAM_TABLE]]", table(["Forecaster", "Parameter", "Prior median (p10–p90)", "METR-conditioned"], param_rows()))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>METR Evidence in AIFM</title><style>{css}</style></head><body><main>{body}</main></body></html>"""


if __name__ == "__main__":
    narrative = (HERE / "report_text.html").read_text()
    (HERE / "report.html").write_text(build(narrative))
    print("wrote report.html", (HERE / "report.html").stat().st_size // 1024, "KB")
