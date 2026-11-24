"""
Builds the multi-page FitTrack site from the Markdown/CSV documents.

    python build_site.py        (needs: pip install markdown)

Writes charter.html, backlog.html, sprints.html, raci.html, risks.html, burndown.html,
retrospective.html and status-report.html next to index.html. All site files live in the
repo root so they work on GitHub Pages however the repo is uploaded.
"""
import csv
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
REPO = "https://github.com/Mrunali121/fittrack-agile-pm"

PAGES = [
    ("charter", "Charter", "Project Charter"),
    ("backlog", "Backlog", "Product Backlog"),
    ("sprints", "Sprint Plans", "Sprint Planning"),
    ("raci", "RACI", "RACI Matrix"),
    ("risks", "Risk Register", "Risk Register"),
    ("burndown", "Burndown", "Sprint Burndown"),
    ("retrospective", "Retrospective", "Retrospective"),
    ("status-report", "Status Report", "Weekly Status Report"),
]
LINKS = {
    "01-project-charter.md": "charter.html", "02-product-backlog.csv": "backlog.html", "04-raci-matrix.md": "raci.html",
    "05-risk-register.md": "risks.html", "06-sprint-burndown-chart.png": "burndown.html", "07-retrospective.md": "retrospective.html",
    "08-status-report-template.md": "status-report.html", "README.md": "index.html",
}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | FitTrack Agile PM Case Study</title>
<meta name="description" content="FitTrack agile project management case study: {title}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>
"""
FOOT = f"""<footer>
  <div class="wrap">
    <p>FITTRACK - A SELF-DIRECTED AGILE PROJECT MANAGEMENT PORTFOLIO PROJECT. THE PROJECT IS SIMULATED.</p>
    <div class="links"><a href="{REPO}" target="_blank" rel="noopener">GitHub</a><a href="https://mrunali121.github.io/" target="_blank" rel="noopener">Portfolio</a></div>
  </div>
</footer>
"""


def nav(current):
    items = ['<a href="index.html" class="brand">FitTrack</a>']
    for slug, label, _ in PAGES:
        items.append(f'<a href="{slug}.html"' + (' aria-current="page"' if slug == current else "") + f">{label}</a>")
    return '<nav class="topnav" aria-label="Case study pages"><div class="wrap nav-in">' + "".join(items) + "</div></nav>\n"


def pager(slug):
    i = [p[0] for p in PAGES].index(slug)
    a = f'<a class="pg" href="{PAGES[i-1][0]}.html">&larr; {PAGES[i-1][1]}</a>' if i else '<a class="pg" href="index.html">&larr; Overview</a>'
    b = f'<a class="pg" href="{PAGES[i+1][0]}.html">{PAGES[i+1][1]} &rarr;</a>' if i < len(PAGES) - 1 else '<a class="pg" href="index.html">Back to overview &rarr;</a>'
    return f'<div class="pager">{a}{b}</div>'


def page(slug, title, lead, body, scripts=""):
    out = (HEAD.format(title=html.escape(title)) + nav(slug)
           + f'<header class="pagehead"><div class="wrap"><div class="eyebrow">Case study page</div><h1>{html.escape(title)}</h1>'
           + (f'<p class="sub">{lead}</p>' if lead else "") + "</div></header>\n"
           + f'<main class="wrap doc">{body}{pager(slug)}</main>\n' + FOOT + scripts + "</body>\n</html>\n")
    (ROOT / f"{slug}.html").write_text(out, encoding="utf-8")


def md_body(path, drop_h1=True):
    text = Path(path).read_text(encoding="utf-8")
    if drop_h1:
        text = re.sub(r"\s*#\s+.*\n", "", text, count=1)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    def fix(mo):
        key = mo.group(1).split("#")[0].split("/")[-1]
        return f'href="{LINKS[key]}"' if key in LINKS else mo.group(0)
    return re.sub(r'href="([^"]+)"', fix, body)


LEADS = {
    "charter": "Scope, objectives, stakeholders and success criteria, agreed before any code was written.",
    "raci": "Who is responsible, accountable, consulted and informed for each deliverable.",
    "risks": "Reviewed at every sprint planning session, not written once and forgotten.",
    "retrospective": "What went well, what did not, and the owned action items.",
    "status-report": "The weekly stakeholder format, filled in with a real example.",
}
for slug, src in (("charter", "01-project-charter.md"), ("raci", "04-raci-matrix.md"), ("risks", "05-risk-register.md"),
                  ("retrospective", "07-retrospective.md"), ("status-report", "08-status-report-template.md")):
    page(slug, dict((p[0], p[2]) for p in PAGES)[slug], LEADS[slug], md_body(src))

# ---- backlog: CSV -> filterable table ----
rows = list(csv.DictReader(open(ROOT / "02-product-backlog.csv", encoding="utf-8")))
cols = list(rows[0].keys())
tbl = '<div class="filters" role="group" aria-label="Filter by sprint"><button class="chipb" data-s="All" aria-pressed="true">All</button>'
tbl += "".join(f'<button class="chipb" data-s="{s}" aria-pressed="false">{s}</button>' for s in sorted({r["Sprint"] for r in rows}))
tbl += '</div><div class="tablewrap"><table id="bk"><thead><tr>' + "".join(f"<th>{html.escape(c)}</th>" for c in cols) + "</tr></thead><tbody>"
for r in rows:
    tbl += f'<tr data-s="{html.escape(r["Sprint"])}">' + "".join(
        f'<td class="c-{re.sub("[^a-z]", "", c.lower())} v-{re.sub("[^a-z]", "", r[c].lower())}">{html.escape(r[c])}</td>' for c in cols) + "</tr>"
tbl += "</tbody></table></div>"
pts = sum(int(r["Story Points"]) for r in rows if r["Story Points"].isdigit())
body = (f"<p>{len(rows)} items, {pts} story points in total, prioritised with MoSCoW and sized in story points. Use the buttons to filter by sprint.</p>" + tbl
        + f'<p><a class="btn btn-primary" href="02-product-backlog.csv">Download the CSV</a></p>')
script = """<script>
document.querySelectorAll('.chipb').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.chipb').forEach(x=>x.setAttribute('aria-pressed',x===b));
  document.querySelectorAll('#bk tbody tr').forEach(tr=>{tr.style.display=(b.dataset.s==='All'||tr.dataset.s===b.dataset.s)?'':'none'});
}));
</script>
"""
page("backlog", "Product Backlog", "Prioritised stories with story points, sprint and status.", body, script)

# ---- sprint plans: all three on one page ----
body = '<p class="jump">Jump to: <a href="#sprint-1">Sprint 1</a> · <a href="#sprint-2">Sprint 2</a> · <a href="#sprint-3">Sprint 3</a></p>'
for n in (1, 2, 3):
    body += f'<section class="sp" id="sprint-{n}"><h2 class="sp-h">Sprint {n}</h2>' + md_body(ROOT / "03-sprint-planning" / f"sprint-0{n}-plan.md") + "</section>"
page("sprints", "Sprint Planning", "Capacity-based commitment for each of the three two-week sprints.", body)

# ---- burndown ----
body = ('<figure class="burn"><a href="burndown-chart.png" target="_blank" rel="noopener"><img src="burndown-chart.png" alt="Sprint 2 burndown chart showing the scope-creep jump and recovery"></a>'
        '<figcaption>Sprint 2 burndown. Click the chart to open it full size.</figcaption></figure>'
        '<p>A mid-sprint stakeholder request added 8 story points to Sprint 2. The chart makes the jump visible straight away, and the recovery plan brought the sprint back under control without breaking the sprint goal.</p>'
        f'<p>The chart is generated by a Python script, so the data and annotations are reproducible rather than a static image: <a href="{REPO}/blob/main/generate_burndown_chart.py" target="_blank" rel="noopener">generate_burndown_chart.py</a>.</p>')
page("burndown", "Sprint Burndown", "How a scope-creep incident showed up, and how it was handled.", body)
print("Built", len(PAGES), "pages")
