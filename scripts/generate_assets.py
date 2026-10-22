"""Generates the self-hosted SVG assets for the GitHub profile README.

Run:  python generate_assets.py
Output: ../assets/*.svg

Everything is plain SVG (no JS, no external fonts, no third-party services) so it
renders on github.com via <img>. Animation is SMIL only, kept subtle.
Colours/tokens mirror shubham-ai-lab.vercel.app.
"""
import html
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

# ---- design tokens (from the portfolio) ------------------------------------
BG = "#070a14"
CARD = "#0b1020"
CARD2 = "#0e1530"
BORDER = "#1b2548"
TEXT = "#e8ecf8"
MUTED = "#8b95b5"
DIM = "#5d6a93"
BLUE = "#5b8cff"
PURPLE = "#8b5cf6"
GREEN = "#22c55e"
AMBER = "#f5b83d"
SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"


def esc(s):
    return html.escape(s, quote=False)


def svg(w, h, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{SANS}">\n<defs>\n'
        f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/>'
        f'<stop offset="1" stop-color="{PURPLE}"/></linearGradient>\n{defs}</defs>\n{body}\n</svg>\n'
    )


def save(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", name)


def text(x, y, s, size=13, fill=TEXT, weight=400, mono=False, anchor="start", spacing=0, extra=""):
    fam = f' font-family="{MONO}"' if mono else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}"'
        f' text-anchor="{anchor}"{fam}{ls}{extra}>{s}</text>'
    )


def pulse_dot(cx, cy, color=GREEN, r=3.5):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity=".35">'
        f'<animate attributeName="r" values="{r};{r*2.6};{r}" dur="2.4s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".45;0;.45" dur="2.4s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
    )


def pill(x, y, label, color, w=None, dot=False):
    w = w or (len(label) * 6.4 + (30 if dot else 20))
    body = (
        f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="10" fill="{color}" fill-opacity=".12" '
        f'stroke="{color}" stroke-opacity=".45"/>'
    )
    tx = x + (24 if dot else 10)
    if dot:
        body += pulse_dot(x + 13, y + 10, color, 3)
    body += text(tx, y + 14, label, 9.5, color, 700, mono=True, spacing=1)
    return body, w


def chip(x, y, label, size=11, pad=9, h=22, fill=CARD2, color=MUTED, stroke=BORDER, mono=False):
    cw = size * (0.6 if mono else 0.56)
    w = len(label) * cw + pad * 2
    b = (
        f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}"/>'
        + text(x + pad, y + h / 2 + size * 0.35, esc(label), size, color, 500, mono=mono)
    )
    return b, w


# ---- 1. banner --------------------------------------------------------------
def typing(x, y, phrases, size=16, cw=10, per=4.2):
    total = per * len(phrases)
    eps = 0.0004
    out, defs = "", ""
    for i, p in enumerate(phrases):
        W = len(p) * cw
        s = i * per / total + eps
        td = min(len(p) * 0.075, 2.3) / total
        e = ((i + 1) * per - 0.55) / total
        z = e + 0.25 / total
        kt = f"0;{s:.4f};{s+td:.4f};{e:.4f};{z:.4f};1"
        defs += (
            f'<clipPath id="cp{i}"><rect x="{x}" y="{y-size}" height="{size*1.6}" width="{W if i == 0 else 0}">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" '
            f'values="0;0;{W};{W};0;0"/></rect></clipPath>\n'
        )
        out += (
            f'<text x="{x}" y="{y}" font-size="{size}" font-family="{MONO}" fill="{TEXT}" '
            f'textLength="{W}" lengthAdjust="spacing" clip-path="url(#cp{i})">{esc(p)}</text>\n'
            f'<rect y="{y-size+2}" width="2" height="{size}" fill="{BLUE}" opacity="0">'
            f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" '
            f'values="{x};{x};{x+W};{x+W};{x};{x}"/>'
            f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" '
            f'values="0;1;1;1;0;0"/></rect>\n'
        )
    return out, defs


def banner():
    W, H = 1000, 300
    t_body, t_defs = typing(48, 238, [
        "Agentic AI · LLM Systems · Automation",
        "With humans kept in control.",
        "From automation to agentic AI →",
    ])
    defs = f"""
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
<path d="M40 0H0V40" fill="none" stroke="#111a36" stroke-width="1"/></pattern>
<radialGradient id="glowP"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".30"/>
<stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<radialGradient id="glowB"><stop offset="0" stop-color="{BLUE}" stop-opacity=".26"/>
<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<clipPath id="round"><rect width="{W}" height="{H}" rx="16"/></clipPath>
{t_defs}"""
    body = f"""
<g clip-path="url(#round)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<circle cx="870" cy="40" r="240" fill="url(#glowP)"><animate attributeName="r" values="230;270;230" dur="9s" repeatCount="indefinite"/></circle>
<circle cx="80" cy="300" r="220" fill="url(#glowB)"><animate attributeName="r" values="210;250;210" dur="11s" repeatCount="indefinite"/></circle>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{BORDER}"/>
<rect x="48" y="40" width="198" height="28" rx="7" fill="{CARD}" stroke="{BORDER}"/>
{pulse_dot(64, 54, GREEN, 3)}
{text(76, 58, "AI SYSTEMS ENGINEER", 10.5, TEXT, 700, mono=True, spacing=1.2)}
<text x="{W-48}" y="58" font-size="13" font-weight="800" text-anchor="end" fill="{TEXT}" letter-spacing="1">SHUBHAM <tspan fill="url(#g)">AI LAB</tspan></text>
<text x="48" y="126" font-size="35" font-weight="800" fill="{TEXT}" letter-spacing="-.5">I build AI systems that <tspan fill="{BLUE}">reason,</tspan> <tspan fill="{PURPLE}">use tools,</tspan></text>
<text x="48" y="172" font-size="35" font-weight="800" fill="{TEXT}" letter-spacing="-.5">and operate in <tspan fill="{BLUE}">real business workflows.</tspan></text>
<rect x="48" y="190" width="64" height="3" rx="1.5" fill="url(#g)"/>
{t_body}
<circle cx="52" cy="274" r="3" fill="{GREEN}"/>
{text(64, 278, "Open to AI Engineering · Agentic AI · AI Solutions · Forward Deployed Engineer roles", 11.5, MUTED)}
{text(W-48, 278, "shubham-ai-lab.vercel.app", 11, DIM, mono=True, anchor="end")}
"""
    save("banner.svg", svg(W, H, body, defs))


# ---- 2. metrics -------------------------------------------------------------
def glyph(kind):
    s = f'fill="none" stroke="{BLUE}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    paths = {
        "clock": f'<circle cx="14" cy="14" r="7" {s}/><path d="M14 10v4.5l3 1.5" {s}/>',
        "layers": f'<path d="M14 7l8 4-8 4-8-4z" {s}/><path d="M6 15l8 4 8-4" {s}/>',
        "refresh": f'<path d="M20 11a6.5 6.5 0 0 0-11.5-2M8 17a6.5 6.5 0 0 0 11.5 2" {s}/><path d="M20 6v5h-5M8 22v-5h5" {s}/>',
        "trend": f'<path d="M6 19l5-5 3 3 8-8" {s}/><path d="M17 9h5v5" {s}/>',
        "scan": f'<path d="M7 11V8a1 1 0 0 1 1-1h3M17 7h3a1 1 0 0 1 1 1v3M21 17v3a1 1 0 0 1-1 1h-3M11 21H8a1 1 0 0 1-1-1v-3" {s}/><path d="M10 14h8" {s}/>',
        "shield": f'<path d="M14 6l7 3v5c0 4-3 7-7 8-4-1-7-4-7-8V9z" {s}/><path d="M11 14l2.2 2.2L17 12" {s}/>',
    }
    return paths[kind]


def metrics():
    items = [
        ("clock", "2.8+", ["Years building", "production", "automation & AI"]),
        ("layers", "10+", ["Automation", "frameworks", "shipped and run"]),
        ("refresh", "3,000+", ["Transactions /", "month handled"]),
        ("trend", "~80%", ["Manual effort", "reduced"]),
        ("scan", "~95%", ["Invoice extraction", "accuracy (10 → 2", "min each)"]),
        ("shield", "~40%", ["Exception-handling", "effort cut with LLM", "decisioning"]),
    ]
    W, H, gap = 1000, 118, 12
    tw = (W - gap * 5) / 6
    body = ""
    for i, (g, val, lines) in enumerate(items):
        x = i * (tw + gap)
        body += f'<g transform="translate({x:.1f},0)">'
        body += f'<rect x=".5" y=".5" width="{tw-1:.1f}" height="{H-1}" rx="13" fill="{CARD}" stroke="{BORDER}"/>'
        body += f'<rect x="13" y="14" width="30" height="30" rx="8" fill="{CARD2}" stroke="{BORDER}"/>'
        body += f'<g transform="translate(14,15)">{glyph(g)}</g>'
        body += text(52, 37, val, 23, TEXT, 800, extra=' letter-spacing="-.5"')
        for j, ln in enumerate(lines):
            body += text(14, 62 + j * 14, esc(ln), 10.5, MUTED)
        body += "</g>"
    save("metrics.svg", svg(W, H, body))


# ---- 3. status dashboard ----------------------------------------------------
def status_svg(week=6, total=7, version="v0.4", next_text="public demo (v1.0)", projects=10,
               latest="Agent Blackbox · demo live"):
    W, H = 1000, 276
    lw, rx0 = 440, 464
    rw = W - rx0
    # left: currently building
    p, pw = pill(lw - 24 - 106, 22, "IN PROGRESS", GREEN, 106, dot=True)
    c1, w1 = chip(24, 118, "WhatsApp", 11, mono=True)
    c2, w2 = chip(24 + w1 + 6, 118, "Excel", 11, mono=True)
    c3, w3 = chip(24 + w1 + w2 + 12, 118, "PDF", 11, mono=True)
    flow, x = "", 24
    for k, lab in enumerate(["AI processing", "Agent proposals", "Owner approval"]):
        cc, ww = chip(x, 150, lab, 11, stroke=BLUE if k == 0 else BORDER, color=TEXT if k == 0 else MUTED)
        flow += cc
        x += ww
        if k < 2:
            flow += text(x + 4, 165, "→", 11, DIM)
            x += 16
    left = f"""
<rect x=".5" y=".5" width="{lw-1}" height="{H-1}" rx="14" fill="{CARD}" stroke="{BORDER}"/>
{text(24, 38, "CURRENTLY BUILDING", 11, MUTED, 700, mono=True, spacing=1.5)}
{p}
{text(24, 80, "Opspilot", 26, TEXT, 800, extra=' letter-spacing="-.4"')}
{text(24, 102, "AI back office for small businesses.", 13, MUTED)}
{c1}{c2}{c3}
{flow}
{text(24, 200, esc("Next: " + next_text), 11.5, MUTED, mono=True)}
{text(24, 230, "Progress", 11.5, MUTED)}
{text(lw-24, 230, esc(f"Week {week} of {total} · {version}"), 11.5, TEXT, 700, mono=True, anchor="end")}
<rect x="24" y="242" width="{lw-48}" height="8" rx="4" fill="{CARD2}" stroke="{BORDER}"/>
<rect x="24" y="242" width="{(lw-48)*week/total:.1f}" height="8" rx="4" fill="url(#g)">
<animate attributeName="width" from="0" to="{(lw-48)*week/total:.1f}" dur="1.8s" begin="0.3s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1"/></rect>
"""
    rows = [
        ("Portfolio", "Online", GREEN),
        ("GitHub", "Shubham261299", TEXT),
        ("Projects", str(projects), TEXT),
        ("AI experiments", "Active", GREEN),
        ("Building", "Opspilot", TEXT),
        ("Latest", latest, TEXT),
        ("Exploring", "Agent evaluation, MCP security", TEXT),
    ]
    op, _ = pill(rw - 24 - 84, 22, "ONLINE", GREEN, 84, dot=True)
    right = f'<g transform="translate({rx0},0)">'
    right += f'<rect x=".5" y=".5" width="{rw-1}" height="{H-1}" rx="14" fill="{CARD}" stroke="{BORDER}"/>'
    right += text(24, 38, "SYSTEM STATUS", 11.5, TEXT, 800, mono=True, spacing=1.6) + op
    for i, (k, v, col) in enumerate(rows):
        y = 78 + i * 29
        right += f'<line x1="24" y1="{y-16}" x2="{rw-24}" y2="{y-16}" stroke="{BORDER}"/>'
        right += text(24, y, k, 12.5, MUTED)
        right += text(rw - 24, y, esc(v), 12.5, col, 600, anchor="end")
    right += "</g>"
    return svg(W, H, left + right)


def status(**kw):
    save("status.svg", status_svg(**kw))


# ---- 4. section headers -----------------------------------------------------
def header(name, label, title, sub=""):
    W = 1000
    H = 92 if sub else 66
    body = (
        text(0, 16, label, 11, BLUE, 700, mono=True, spacing=2.2)
        + text(0, 50, esc(title), 30, TEXT, 800, extra=' letter-spacing="-.6"')
    )
    if sub:
        body += text(0, 76, esc(sub), 13.5, MUTED)
    body += (
        f'<rect x="0" y="{H-2}" width="1000" height="1.5" fill="url(#fade)"/>'
    )
    defs = (
        f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity=".7"/>'
        f'<stop offset=".35" stop-color="{PURPLE}" stop-opacity=".35"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>'
    )
    save(name, svg(W, H, body, defs))


# ---- 5. project cards -------------------------------------------------------
PROJECTS = [
    ("01", "Agentic Case-Routing Orchestrator",
     "Routes support cases to pluggable AI agents, with a critic, bounded re-planning and a human approval gate. State survives a restart.",
     ["LangGraph", "FastAPI", "Ollama", "SQLite"], ("DOCS ONLY", AMBER)),
    ("02", "Enterprise MCP Layer",
     "Two MCP servers (Salesforce + Smartsheet) giving AI agents controlled, audited access to business data: identity, permissions, audit trail.",
     ["MCP SDK", "PostgreSQL", "Docker"], ("DOCS ONLY", AMBER)),
    ("03", "Agentic Tool Orchestrator",
     "A LangGraph ReAct agent with 12 sandboxed tools behind a FastAPI service, scored by an LLM-as-judge.",
     ["LangGraph", "Claude", "FastAPI", "Pydantic"], ("OPEN SOURCE", GREEN)),
    ("04", "Opspilot",
     "Human-in-the-loop AI back office: messy WhatsApp orders, Excel stock and PDF invoices become proposals for owner approval.",
     ["FastAPI", "PostgreSQL", "LangGraph", "Docker"], ("IN PROGRESS", BLUE)),
    ("05", "Self-Healing Invoice Automation",
     "Browser automation that recovers when a portal's UI changes: sends the live DOM to Claude, gets a new selector and retries.",
     ["Playwright", "Claude API", "Streamlit"], ("OPEN SOURCE", GREEN)),
    ("06", "Daybook",
     "Local-first work journal: reads Git commits and notes, and a local LLM writes daily, weekly and monthly summaries. In daily use.",
     ["FastAPI", "SQLite", "GitPython", "Ollama"], ("OPEN SOURCE", GREEN)),
    ("07", "SOP Assistant",
     "Local RAG over SOP PDFs with context-only answers, explicit refusals and page-level citations.",
     ["LangChain", "FAISS", "Hugging Face"], ("OPEN SOURCE", GREEN)),
    ("08", "Decision Intelligence Lab",
     "Research framework for evaluating LLMs as structured decision makers: typed contracts, rules vs LLM strategies, policy checks and a 30-case benchmark.",
     ["Python", "Pydantic", "Ollama", "Streamlit"], ("OPEN SOURCE", GREEN)),
    ("09", "Agent Blackbox",
     "A flight recorder for AI agents: records every step, checks the run, shows where it failed and measures whether a fix helped or hurt.",
     ["Python", "FastAPI", "React", "Ollama", "Docker"], ("OPEN SOURCE", GREEN)),
    ("10", "The Last Witness",
     "A local detective game: question three staff members, compare twelve records, rebuild the timeline and file an evidence-backed report.",
     ["Next.js", "TypeScript", "Python", "FastAPI", "Ollama"], ("V1 PROTOTYPE", PURPLE)),
]
EXTRA_PILLS = {"09": ("RECORDED DEMO", BLUE)}


def project_cards():
    W, H = 490, 176
    for idx, (num, name, desc, stack, (tag, tcol)) in enumerate(PROJECTS):
        fname = f"card-{num}.svg"
        lines = textwrap.wrap(desc, 66)[:3]
        tw = len(tag) * 6.4 + (30 if tag == "IN PROGRESS" else 20)
        pl, _ = pill(W - 20 - tw, 16, tag, tcol, tw, dot=(tag == "IN PROGRESS"))
        if num in EXTRA_PILLS:
            elab, ecol = EXTRA_PILLS[num]
            ew = len(elab) * 6.4 + 20
            epl, _ = pill(W - 20 - tw - 8 - ew, 16, elab, ecol, ew)
            pl += epl
        body = f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{CARD}" stroke="{BORDER}"/>'
        body += f'<rect x="1" y="1" width="{W-2}" height="3" rx="1.5" fill="url(#g)" opacity=".55"/>'
        body += text(20, 36, num, 11, BLUE, 700, mono=True, spacing=1.5) + pl
        body += text(20, 62, esc(name), 17, TEXT, 800, extra=' letter-spacing="-.2"')
        for j, ln in enumerate(lines):
            body += text(20, 86 + j * 17, esc(ln), 12.2, MUTED)
        x = 20
        for s in stack:
            c, w = chip(x, H - 38, s, 10, pad=8, h=22, mono=True)
            body += c
            x += w + 6
        save(fname, svg(W, H, body))
    # catalogue CTA
    body = (
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{CARD}" stroke="url(#g)" stroke-width="1.5"/>'
        + text(20, 36, "CATALOGUE", 11, BLUE, 700, mono=True, spacing=1.5)
        + text(20, 70, "See the full lab", 22, TEXT, 800, extra=' letter-spacing="-.3"')
        + text(20, 96, "Architecture, engineering decisions and", 12.2, MUTED)
        + text(20, 113, "demos for every system.", 12.2, MUTED)
        + f'<rect x="20" y="{H-50}" width="206" height="32" rx="9" fill="url(#g)"/>'
        + text(123, H - 29, "shubham-ai-lab.vercel.app →", 11.5, "#fff", 700, mono=True, anchor="middle")
    )
    save("card-catalogue.svg", svg(W, H, body))
    WW, HH = 1000, 104
    body = (
        f'<rect x="1" y="1" width="{WW-2}" height="{HH-2}" rx="14" fill="{CARD}" stroke="url(#g)" stroke-width="1.5"/>'
        + text(24, 34, "CATALOGUE", 11, BLUE, 700, mono=True, spacing=1.5)
        + text(24, 62, "See the full lab", 22, TEXT, 800, extra=' letter-spacing="-.3"')
        + text(24, 84, "Architecture, engineering decisions and write-ups for every system, in one place.", 12.5, MUTED)
        + f'<rect x="{WW-24-232}" y="{(HH-34)//2}" width="232" height="34" rx="9" fill="url(#g)"/>'
        + text(WW - 24 - 116, (HH - 34) // 2 + 22, "shubham-ai-lab.vercel.app →", 12, "#fff", 700, mono=True, anchor="middle")
    )
    save("card-catalogue-wide.svg", svg(WW, HH, body))


# ---- 5b. development status board ----
BOARD_DATE = "22 Oct 2026"
BOARD = [
    ("01", "Agentic Case-Routing Orchestrator", ("DOCS ONLY", AMBER), "Deployed internally · source proprietary"),
    ("02", "Enterprise MCP Layer", ("DOCS ONLY", AMBER), "Deployed internally · source proprietary"),
    ("03", "Agentic Tool Orchestrator", ("OPEN SOURCE", GREEN), "Working · 12 sandboxed tools, LLM-as-judge evaluation"),
    ("04", "Opspilot", ("IN PROGRESS", BLUE), "Week 6 of 7 done (v0.4) · public demo next"),
    ("05", "Self-Healing Invoice Automation", ("OPEN SOURCE", GREEN), "Working demo · recovers from simulated UI breakage"),
    ("06", "Daybook", ("OPEN SOURCE", GREEN), "In daily use · local LLM summaries · MIT"),
    ("07", "SOP Assistant", ("OPEN SOURCE", GREEN), "Working local RAG · page-level citations"),
    ("08", "Decision Intelligence Lab", ("OPEN SOURCE", GREEN), "Software-first release · offline demo app"),
    ("09", "Agent Blackbox", ("OPEN SOURCE", GREEN), "Recorded demo live · Docker stack · MIT"),
    ("10", "The Last Witness", ("V1 PROTOTYPE", PURPLE), "V1 approved 14 Oct 2026 · replayable case"),
]


def board_svg(rows=None, date=None):
    rows = BOARD if rows is None else rows
    date = date or BOARD_DATE
    W, rh, top = 1000, 36, 52
    H = top + rh * len(rows) + 40
    body = f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{CARD}" stroke="{BORDER}"/>'
    body += text(24, 32, "#", 10.5, DIM, 700, mono=True, spacing=1.5)
    body += text(62, 32, "SYSTEM", 10.5, DIM, 700, mono=True, spacing=1.5)
    body += text(372, 32, "STATUS", 10.5, DIM, 700, mono=True, spacing=1.5)
    body += text(520, 32, "WHERE IT STANDS", 10.5, DIM, 700, mono=True, spacing=1.5)
    for i, (num, name, (tag, col), stage) in enumerate(rows):
        y = top + i * rh
        body += f'<line x1="24" y1="{y}" x2="{W-24}" y2="{y}" stroke="{BORDER}"/>'
        body += text(24, y + 23, num, 11, BLUE, 700, mono=True)
        body += text(62, y + 23, esc(name), 13.5, TEXT, 700)
        pl, _ = pill(372, y + 8, tag, col, None, dot=(tag == "IN PROGRESS"))
        body += pl
        body += text(520, y + 23, esc(stage), 12.5, MUTED)
    body += text(24, H - 16, f"Status as of {date}", 10.5, DIM, mono=True)
    return svg(W, H, body)


def board(**kw):
    save("board.svg", board_svg(**kw))


# ---- 6. philosophy ----------------------------------------------------------
def principles():
    items = [
        ("01", "Ground the model", "Facts before generation."),
        ("02", "Give agents tools", "Intelligence becomes useful when it can interact."),
        ("03", "Keep humans in control", "Automation ≠ removing accountability."),
        ("04", "Make state durable", "Agents should survive failures."),
        ("05", "Measure the system", "Evaluation > vibes."),
    ]
    W, H, gap = 1000, 132, 12
    tw = (W - gap * 4) / 5
    body = ""
    for i, (n, t, s) in enumerate(items):
        x = i * (tw + gap)
        body += f'<g transform="translate({x:.1f},0)">'
        body += f'<rect x=".5" y=".5" width="{tw-1:.1f}" height="{H-1}" rx="13" fill="{CARD}" stroke="{BORDER}"/>'
        body += f'<rect x="14" y="14" width="30" height="24" rx="7" fill="{CARD2}" stroke="{BORDER}"/>'
        body += text(29, 30, n, 10.5, BLUE, 700, mono=True, anchor="middle")
        body += text(14, 62, esc(t), 13.5, TEXT, 700)
        for j, ln in enumerate(textwrap.wrap(s, 24)[:3]):
            body += text(14, 82 + j * 15, esc(ln), 11, MUTED)
        body += "</g>"
    save("principles.svg", svg(W, H, body))


# ---- 7. toolbox -------------------------------------------------------------
def toolbox():
    groups = [
        ("AGENTIC AI & LLMS", ["LangGraph", "LangChain", "Multi-agent orchestration", "ReAct & tool calling",
                               "Model Context Protocol (MCP)", "Human-in-the-loop", "LLM-as-judge evaluation", "Agent evaluation", "Observability & tracing", "Guardrails"]),
        ("MODELS & RETRIEVAL", ["Claude", "OpenAI", "Gemini", "Hugging Face", "Ollama (local LLMs)", "RAG", "FAISS",
                                "ChromaDB", "Embeddings"]),
        ("BACKEND & INTEGRATION", ["Python", "FastAPI", "Pydantic", "REST APIs", "SQL Server", "PostgreSQL", "SQLite", "Docker"]),
        ("AUTOMATION & DOCUMENT AI", ["Playwright", "Selenium", "UiPath", "OCR / IDP", "OpenCV", "PyMuPDF", "Power Automate"]),
        ("DATA & TOOLING", ["pandas", "Power BI", "Git", "Linux", "Streamlit", "TypeScript", "React", "Next.js", "Claude Code", "Cursor"]),
        ("CERTIFICATIONS", None),
    ]
    certs = [
        "Full Stack Generative & Agentic AI with Python (Udemy)",
        "UiPath Automation Developer Professional Training (UiPath Academy)",
        "Python (Kaggle)",
    ]
    W, gap, cols = 1000, 12, 3
    bw = (W - gap * 2) / 3
    pad = 16
    layouts = []
    for title, items in groups:
        inner = bw - pad * 2
        if items is None:
            lines = []
            for c in certs:
                lines += textwrap.wrap(c, 44)
                lines.append("")
            lines = lines[:-1]
            h = 52 + len(lines) * 15 + 10
            layouts.append((title, ("certs", lines), h))
            continue
        x = y = 0
        placed = []
        for it in items:
            w = len(it) * 6.3 + 18
            if x + w > inner:
                x, y = 0, y + 30
            placed.append((it, x, y))
            x += w + 6
        layouts.append((title, ("chips", placed), 52 + y + 22 + 12))
    row_h = [max(layouts[0][2], layouts[1][2], layouts[2][2]), max(layouts[3][2], layouts[4][2], layouts[5][2])]
    H = row_h[0] + row_h[1] + gap
    body = ""
    for i, (title, data, _) in enumerate(layouts):
        r, c = divmod(i, cols)
        x0 = c * (bw + gap)
        y0 = 0 if r == 0 else row_h[0] + gap
        bh = row_h[r]
        body += f'<g transform="translate({x0:.1f},{y0})">'
        body += f'<rect x=".5" y=".5" width="{bw-1:.1f}" height="{bh-1}" rx="13" fill="{CARD}" stroke="{BORDER}"/>'
        body += text(pad, 30, esc(title), 10.5, BLUE, 700, mono=True, spacing=1.6)
        if data[0] == "chips":
            for it, cx, cy in data[1]:
                cc, _ = chip(pad + cx, 44 + cy, it, 11, pad=9, h=22)
                body += cc
        else:
            for j, ln in enumerate(data[1]):
                body += text(pad, 56 + j * 15, esc(ln), 11.5, MUTED if ln else MUTED)
        body += "</g>"
    save("toolbox.svg", svg(W, H, body))


# ---- 8. career evolution ----------------------------------------------------
def evolution():
    steps = [
        ("2019", "Data Science", "Python, SQL", False),
        ("2023", "Automation", "RPA, Power BI", False),
        ("2024", "Intelligent Automation", "OCR, APIs", False),
        ("2025", "GenAI", "RAG, LLMs", False),
        ("2026", "Agentic AI", "LangGraph, MCP", True),
        ("Next", "AI Systems · FDE", "Customer-facing AI", None),
    ]
    W, H = 1000, 170
    n = len(steps)
    xs = [W / n * (i + 0.5) for i in range(n)]
    body = f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{CARD}" stroke="{BORDER}"/>'
    body += (
        f'<line x1="{xs[0]}" y1="52" x2="{xs[-1]}" y2="52" stroke="{BORDER}" stroke-width="2"/>'
        f'<line x1="{xs[0]}" y1="52" x2="{xs[4]}" y2="52" stroke="url(#g)" stroke-width="2" stroke-dasharray="6 6">'
        f'<animate attributeName="stroke-dashoffset" from="24" to="0" dur="2.4s" repeatCount="indefinite"/></line>'
    )
    for i, (yr, t, s, cur) in enumerate(steps):
        x = xs[i]
        if cur is None:
            body += f'<circle cx="{x}" cy="52" r="15" fill="{BG}" stroke="{BLUE}" stroke-dasharray="3 3"/>'
        elif cur:
            body += (
                f'<circle cx="{x}" cy="52" r="15" fill="none" stroke="{BLUE}" opacity=".5">'
                f'<animate attributeName="r" values="15;24;15" dur="2.6s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values=".55;0;.55" dur="2.6s" repeatCount="indefinite"/></circle>'
                f'<circle cx="{x}" cy="52" r="15" fill="{CARD2}" stroke="{BLUE}" stroke-width="1.8"/>'
            )
        else:
            body += f'<circle cx="{x}" cy="52" r="15" fill="{CARD2}" stroke="{BORDER}" stroke-width="1.5"/>'
        body += f'<circle cx="{x}" cy="52" r="4" fill="{BLUE if cur is not False else DIM}"/>'
        body += text(x, 98, yr, 14, TEXT if cur else TEXT, 800, anchor="middle")
        body += text(x, 118, esc(t), 11.5, TEXT, 600, anchor="middle")
        body += text(x, 135, esc(s), 10.5, MUTED, anchor="middle")
    save("evolution.svg", svg(W, H, body))


# ---- 9. buttons -------------------------------------------------------------
def buttons():
    def btn(name, label, w, primary=False):
        body = (
            f'<rect x="1" y="1" width="{w-2}" height="38" rx="10" fill="url(#g)"/>'
            if primary
            else f'<rect x=".5" y=".5" width="{w-1}" height="39" rx="10" fill="{CARD}" stroke="{BORDER}"/>'
        )
        body += text(w / 2, 25, esc(label), 13, "#fff" if primary else TEXT, 700, anchor="middle")
        save(name, svg(w, 40, body))

    btn("btn-portfolio.svg", "Explore my work  →", 190, primary=True)
    btn("btn-linkedin.svg", "LinkedIn", 120)
    btn("btn-email.svg", "Email", 110)
    btn("btn-site.svg", "Portfolio", 120)
    btn("btn-demo.svg", "Agent Blackbox · recorded demo  →", 292, primary=True)


if __name__ == "__main__":
    banner()
    metrics()
    status()
    header("h-systems.svg", "FEATURED SYSTEMS", "Real systems. Real impact.",
           "AI agents, automation and intelligent systems built for actual business workflows.")
    header("h-board.svg", "DEVELOPMENT STATUS", "Where each system stands",
           "What is shipped, what is a prototype and what is still being built.")
    header("h-philosophy.svg", "ENGINEERING PHILOSOPHY", "How I build",
           "Principles I follow while building agentic AI systems.")
    header("h-toolbox.svg", "TOOLBOX", "What I build with")
    header("h-evolution.svg", "CAREER EVOLUTION", "Automation → GenAI → Agentic AI",
           "Each step added a layer: reliable automation first, then documents and APIs, then LLMs, then agents with human oversight.")
    header("h-activity.svg", "ACTIVITY", "Building in public")
    header("h-connect.svg", "LET'S TALK", "Let's build something impactful.")
    project_cards()
    board()
    principles()
    toolbox()
    evolution()
    buttons()
