"""Builds the portfolio site from src/source.html.

src/source.html holds every piece of content. This script splits it into a
short home page, an About page and one page per tool, with shared CSS and JS.
Run:  python3 build.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "src", "source.html"), encoding="utf-8").read()

NAME = "Ajanth Sri Kathirkamanthan"

# Tool pages, in the order visitors step through them.
TOOLS = [
    # (case id in source, file slug, has demo)
    ("contract", "contract-analysis", True),
    ("market", "market-intelligence", False),
    ("backlog", "backlog-hub", True),
    ("supplier", "supplier-framework", False),
    ("toolkit", "po-toolkit", False),
    ("preppo", "preppo", True),
    ("tamil", "tamil-app", False),
]
SLUG = {cid: slug for cid, slug, _ in TOOLS}


# ---------- helpers to cut blocks out of the source ----------
def block(start_marker, end_tag, src=SRC):
    i = src.index(start_marker)
    j = src.index(end_tag, i) + len(end_tag)
    return src[i:j]


def section_by_id(sid):
    m = re.search(r'<section[^>]*\bid="%s"[^>]*>' % sid, SRC)
    j = SRC.index("</section>", m.start()) + len("</section>")
    return SRC[m.start():j]


def article(cid):
    return block('<article class="case" id="%s"' % cid, "</article>")


def tile_info():
    """Title, result line and icon for each tool, read from the work tiles."""
    info = {}
    for m in re.finditer(r'<a class="tile[^"]*" href="#(\w+)"[^>]*>(.*?)</a>', SRC, re.S):
        cid, inner = m.group(1), m.group(2)
        info[cid] = {
            "title": re.search(r"<h3>(.*?)</h3>", inner).group(1),
            "result": re.search(r'<p class="result">(.*?)</p>', inner).group(1),
            "icon": re.search(r'<use href="#(i-[\w-]+)"/>', inner).group(1),
        }
    return info


def summary_text(art):
    m = re.search(r'<p class="summary">(.*?)</p>', art, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


# ---------- shared pieces ----------
CSS = SRC[SRC.index("<style>") + 7:SRC.index("</style>")]
CSS += r"""
/* ---------- Multi page additions ---------- */
/* Hand drawn underline under the headline */
.scribble-wrap { position: relative; display: inline-block; }
.scribble { position: absolute; left: -2%; bottom: -0.22em; width: 104%; height: 0.38em; overflow: visible; }
.scribble path { fill: none; stroke: var(--brand); stroke-width: 3; stroke-linecap: round; opacity: .55; stroke-dasharray: 400; stroke-dashoffset: 0; animation: draw 1.1s .5s ease both; }
@keyframes draw { from { stroke-dashoffset: 400; } to { stroke-dashoffset: 0; } }
@media (max-width: 720px) { .scribble-wrap { display: inline; } .scribble { display: none; } }
@media (prefers-reduced-motion: reduce) { .scribble path { animation: none; } }

/* Home: compact approach teaser */
.flowrow { list-style: none; padding: 0; margin: 0 0 32px; display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.flowrow li { display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 17px; }
.flowrow li .icon-tile { width: 40px; height: 40px; box-shadow: none; }
.flowrow .arrow { color: var(--fg-3); font-weight: 400; }
.flowrow .arrow svg { width: 18px; height: 18px; }

/* Page header for inner pages */
.pagehead { padding-block: 56px 8px; }
.crumbs { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 14px; color: var(--fg-3); margin-bottom: 16px; }
.crumbs a { color: var(--fg-2); text-decoration: none; font-weight: 500; }
.crumbs a:hover { color: var(--brand-strong); }
.pagehead h1 { font-size: clamp(34px, 4.6vw, 48px); letter-spacing: -0.03em; }
.pagehead .sub { font-size: 19px; color: var(--fg-2); max-width: 40em; margin-top: 14px; }

/* Tool pages */
.case-page { padding-block: 40px 24px; }
.case-head h1 { font-size: clamp(30px, 4vw, 40px); letter-spacing: -0.03em; }
.pn { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 16px; margin-top: 32px; }
.pn a { display: flex; flex-direction: column; gap: 6px; padding: 20px 22px; border: 1px solid var(--line); border-radius: 14px; background: var(--bg); text-decoration: none; color: var(--fg); box-shadow: var(--shadow-xs); transition: border-color .2s, box-shadow .2s, transform .2s; }
.pn a:hover { border-color: var(--brand-ring); box-shadow: var(--shadow-md); transform: translateY(-2px); }
.pn .k { font-size: 13px; font-weight: 600; color: var(--brand-strong); display: inline-flex; align-items: center; gap: 6px; }
.pn .k svg { width: 16px; height: 16px; }
.pn .next { text-align: right; align-items: flex-end; }
.pn .prev .k svg { transform: rotate(180deg); }
.pn h3 { font-size: 18px; }
.pn p { color: var(--fg-2); font-size: 14px; }
.backall { display: inline-flex; align-items: center; gap: 6px; margin-top: 20px; font-weight: 600; font-size: 15px; color: var(--brand-strong); text-decoration: none; }
.backall svg { width: 16px; height: 16px; transform: rotate(180deg); }
.nav a.current { color: var(--brand-strong); background: var(--brand-soft); }
.case-page + #contact { padding-block: 48px 72px; }

/* Work dropdown */
.dd { position: relative; }
.dd-btn { display: inline-flex; align-items: center; gap: 4px; font: 600 15px var(--sans); color: var(--fg-2); background: none; border: 0; padding: 8px 12px; border-radius: 6px; cursor: pointer; }
.dd-btn:hover, .dd-btn[aria-expanded="true"] { background: var(--bg-2); color: var(--fg); }
.dd-btn.current { color: var(--brand-strong); background: var(--brand-soft); }
.dd-btn svg { width: 16px; height: 16px; transition: transform .2s; }
.dd-btn[aria-expanded="true"] svg { transform: rotate(180deg); }
.dd-menu { position: absolute; top: calc(100% + 10px); left: -12px; width: min(680px, calc(100vw - 48px)); display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 8px 16px; padding: 16px; background: var(--bg); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow-xl); z-index: 40; animation: pop .15s ease; }
.dd-menu::before { content: ""; position: absolute; left: 0; right: 0; top: -12px; height: 12px; }
.dd-col { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.dd-h { font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--fg-3); padding: 4px 10px 6px; }
.dd-item { display: grid; grid-template-columns: 40px minmax(0,1fr); gap: 12px; align-items: start; padding: 10px; border-radius: 10px; text-decoration: none; color: var(--fg); }
.dd-item:hover, .dd-item:focus-visible { background: var(--bg-2); }
.dd-item[aria-current="page"] { background: var(--brand-soft); }
.dd-item .icon-tile { width: 40px; height: 40px; box-shadow: none; }
.dd-item b { display: block; font-size: 15px; font-weight: 600; }
.dd-item small { display: block; font-size: 13px; color: var(--fg-3); line-height: 1.45; margin-top: 2px; }
.dd-all { display: inline-flex; align-items: center; gap: 6px; margin: 10px 10px 4px; font-size: 14px; font-weight: 600; color: var(--brand-strong); text-decoration: none; }
.dd-all svg { width: 16px; height: 16px; }

/* Phone menu */
.menu-btn { display: none; }
.mobile-menu { border-top: 1px solid var(--line); background: var(--bg); max-height: calc(100vh - 68px); overflow-y: auto; }
.topbar .mobile-menu .container { height: auto; padding-block: 16px 24px; display: flex; flex-direction: column; align-items: stretch; gap: 8px; }
.mobile-menu .dd-h { padding: 8px 0 2px; }
.m-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 8px; }
.m-tool { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; text-decoration: none; color: var(--fg); font-size: 14px; font-weight: 600; min-width: 0; }
.m-tool svg { width: 18px; height: 18px; color: var(--brand-strong); }
.m-tool[aria-current="page"] { background: var(--brand-soft); border-color: var(--brand-ring); }
.m-links { display: flex; flex-direction: column; margin-top: 8px; border-top: 1px solid var(--line); }
.m-links a { padding: 14px 2px; border-bottom: 1px solid var(--line); color: var(--fg); font-weight: 600; text-decoration: none; }
.m-links a.current { color: var(--brand-strong); }
.m-cta { margin-top: 12px; }
@media (max-width: 1024px) { .menu-btn { display: inline-flex; } }

/* Tool switcher on tool pages */
.switcher { display: flex; gap: 8px; overflow-x: auto; padding: 2px 2px 14px; margin-bottom: 8px; scrollbar-width: thin; }
.sw { display: inline-flex; align-items: center; gap: 8px; flex: none; padding: 7px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--bg); color: var(--fg-2); font-size: 14px; font-weight: 600; text-decoration: none; white-space: nowrap; transition: border-color .15s, color .15s; }
.sw svg { width: 16px; height: 16px; }
.sw:hover { border-color: var(--line-2); color: var(--fg); }
.sw[aria-current="page"] { background: var(--brand-soft); border-color: var(--brand-ring); color: var(--brand-strong); }
@media (max-width: 720px) {
  .pn { grid-template-columns: minmax(0,1fr); }
  .pn .next { text-align: left; align-items: flex-start; }
  .pagehead { padding-block: 36px 0; }
  .case-page { padding-block: 24px 16px; }
}
"""

# One light look: drop the dark theme blocks and the purple.
CSS = re.sub(r'@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme="light"\]\) \{.*?\}\s*\}', "", CSS, flags=re.S)
CSS = re.sub(r':root\[data-theme="dark"\] \{.*?\}', "", CSS, flags=re.S)
CSS = CSS.replace("%237F56D9", "%230B7A5F").replace("#7F56D9", "#0B7A5F").replace("#6941C6", "#096650")
CSS += r"""
/* ================= Workshop wall look ================= */
:root {
  color-scheme: light;
  --page: #FAFAF8;
  --bg: #FFFFFF; --bg-2: #F6F6F2; --bg-3: #EEEEE8;
  --line: #E4E4DD; --line-2: #CDCDC4;
  --fg: #1D1D1B; --fg-2: #47474A; --fg-3: #6C6C68;
  --brand: #0B7A5F; --brand-strong: #096650; --brand-soft: #E3F4EE; --brand-ring: #BFE6D9;
  --marker: #E4462E;
  --note-yellow: #FFE27A; --note-mint: #A8E6CF; --note-pink: #FFC2D1; --note-blue: #A7D3FF;
  --sans: "DM Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
  --display: "Archivo", "DM Sans", system-ui, sans-serif;
  --hand: "Caveat", "Segoe Print", "Comic Sans MS", cursive;
  --shadow-xs: 0 1px 2px rgba(29,29,27,.06);
  --shadow-md: 0 6px 12px -4px rgba(29,29,27,.14);
  --shadow-xl: 0 18px 30px -10px rgba(29,29,27,.22);
}
body { background-color: var(--page); background-image: radial-gradient(#D4D6D9 1.1px, transparent 1.2px); background-size: 22px 22px; }
h1, h2, h3, h4 { font-family: var(--display); }
h1, h2 { font-weight: 800; }
.hero::before { display: none; }
.hero, .section.alt { background: transparent; border-color: transparent; }
.topbar { background: rgba(250,250,248,.92); }
.scrollbar div { background: var(--marker); }

/* Marker annotations */
.eyebrow { display: inline-block; font: 700 25px/1.1 var(--hand); color: var(--marker); transform: rotate(-2deg); transform-origin: left; }
.hero .eyebrow { font-size: 27px; }
.scribble path { stroke: var(--marker); opacity: .9; stroke-width: 3.2; }
.hero h1 .grad { color: var(--fg); }

/* Buttons in ink */
.btn.primary { background: var(--fg); border-color: var(--fg); color: #fff; }
.btn.primary:hover { background: #000; border-color: #000; }
.logo { background: var(--note-yellow); color: var(--fg); transform: rotate(-4deg); box-shadow: var(--shadow-xs); }
.avatar { background: var(--note-yellow); color: var(--fg); }

/* Tape for pinned cards */
.pinned { position: relative; }
.pinned::before { content: ""; position: absolute; top: -11px; left: 50%; width: 92px; height: 24px; transform: translateX(-50%) rotate(-3deg); background: rgba(255,255,255,.62); border: 1px solid rgba(29,29,27,.06); box-shadow: 0 1px 2px rgba(0,0,0,.05); z-index: 2; pointer-events: none; }
.profile { overflow: visible; }
.profile .cover { background: var(--note-yellow); border-radius: 15px 15px 0 0; }

/* Sticky notes */
.metric { border: 0; border-radius: 3px; box-shadow: 0 10px 16px -6px rgba(29,29,27,.25); transition: transform .25s; }
.metric:nth-child(1) { background: var(--note-yellow); transform: rotate(-1.6deg); }
.metric:nth-child(2) { background: var(--note-mint); transform: rotate(1.2deg); }
.metric:nth-child(3) { background: var(--note-pink); transform: rotate(-0.8deg); }
.metric:nth-child(4) { background: var(--note-blue); transform: rotate(1.6deg); }
.metric:hover { transform: rotate(0) translateY(-4px); }
.metric p:first-child, .metric .sub { color: var(--fg-2); }
.metric .num { font-family: var(--display); font-weight: 800; }
.pillars:not(.six) .pillar { border: 0; border-radius: 3px; box-shadow: 0 12px 18px -8px rgba(29,29,27,.28); transition: transform .25s; }
.pillars:not(.six) .pillar:nth-child(1) { background: var(--note-yellow); transform: rotate(-1.4deg); }
.pillars:not(.six) .pillar:nth-child(2) { background: var(--note-mint); transform: rotate(1deg); }
.pillars:not(.six) .pillar:nth-child(3) { background: var(--note-pink); transform: rotate(-0.6deg); }
.pillars:not(.six) .pillar:hover { transform: rotate(0) translateY(-4px); }
.pillars:not(.six) .pillar p { color: var(--fg); }
.pillars:not(.six) .icon-tile { background: rgba(255,255,255,.6); color: var(--fg); box-shadow: none; }
.contact-card { background: var(--note-yellow); border: 0; border-radius: 4px; box-shadow: 0 18px 30px -12px rgba(29,29,27,.3); transform: rotate(-0.4deg); }
.contact-card .sub { color: var(--fg); }
.contact-card .citem { border-color: rgba(29,29,27,.08); }
.case { box-shadow: 0 16px 30px -14px rgba(29,29,27,.22); overflow: visible; }
.case-head { background: linear-gradient(180deg, #FFF7D1, rgba(255,255,255,0) 85%); border-radius: 20px 20px 0 0; }
.tldr dt { color: var(--marker); }
.stackband { background: rgba(255,255,255,.7); }
.chip { font-family: var(--mono); }

@media (prefers-reduced-motion: reduce) { .metric, .pillar { transition: none; } }
/* Problem, Built, Result as three sticky notes on tool pages */
.tldr { background: none; border: 0; gap: 18px; overflow: visible; margin-top: 22px; }
.tldr div { border-radius: 3px; padding: 16px 16px 14px; box-shadow: 0 10px 16px -6px rgba(29,29,27,.25); transition: transform .25s; }
.tldr div:nth-child(1) { background: var(--note-pink); transform: rotate(-1.2deg); }
.tldr div:nth-child(2) { background: var(--note-blue); transform: rotate(0.8deg); }
.tldr div:nth-child(3) { background: var(--note-mint); transform: rotate(-0.6deg); }
.tldr div:hover { transform: rotate(0) translateY(-3px); }
.tldr dt { font: 700 22px/1 var(--hand); letter-spacing: 0; text-transform: none; color: var(--fg); }
.tldr dd { color: var(--fg); font-size: 14.5px; margin-top: 6px; }
@media (prefers-reduced-motion: reduce) { .tldr div { transition: none; } }

/* ================= Professional pass ================= */
/* Platforms strip: one line of evenly sized logos that scrolls slowly */
.stackband .lg { display: block; height: 20px; flex: none; background: var(--fg-2); -webkit-mask: var(--m) center / contain no-repeat; mask: var(--m) center / contain no-repeat; transition: background .2s; }
.stackband .track li:hover .lg { background: var(--c); }
.stackband .track li span:not(.lg) { font-weight: 600; }
.stackband .track ul { gap: 10px; padding: 0 5px; }
.stackband .track li { height: 44px; padding: 0 16px; gap: 8px; }
.stackband .track li img { height: 20px; width: auto; }
.stackband .track li.mark img { height: 18px; max-width: 92px; object-fit: contain; }
.stackband .track li span { font-size: 14px; color: var(--fg-2); }
/* With Reduce Motion on: the same single line, still and swipeable, nothing cut off */
@media (prefers-reduced-motion: reduce) {
  .stackband .marquee { overflow-x: auto; -webkit-mask-image: none; mask-image: none; scrollbar-width: none; }
  .stackband .marquee::-webkit-scrollbar { display: none; }
  .stackband .track, .stackband .track ul { flex-wrap: nowrap; width: max-content; justify-content: flex-start; }
  .stackband .track { padding: 0 16px; }
}
/* Top bar scrolls away with the page instead of staying pinned */
.topbar { position: relative; top: auto; z-index: 20; background: transparent; backdrop-filter: none; }
html { scroll-padding-top: 16px; }
.case { scroll-margin-top: 16px; }
/* Work grid cards: clean white cards with a soft note colour on each icon */
#tiles .tile { border-radius: 14px; box-shadow: 0 6px 14px -10px rgba(29,29,27,.3); }
#tiles .tile:hover { box-shadow: 0 16px 26px -14px rgba(29,29,27,.35); }
#tiles .tile .icon-tile { color: var(--fg); box-shadow: none; }
#tiles .tile:nth-child(4n+1) .icon-tile { background: var(--note-yellow); }
#tiles .tile:nth-child(4n+2) .icon-tile { background: var(--note-mint); }
#tiles .tile:nth-child(4n+3) .icon-tile { background: var(--note-pink); }
#tiles .tile:nth-child(4n+4) .icon-tile { background: var(--note-blue); }
#tiles .tile .tags .badge.brand { background: var(--fg); color: #fff; border-color: var(--fg); }
/* Softer note colours and a quieter background */
:root { --note-yellow: #FFECAE; --note-mint: #D3F0E4; --note-pink: #FDDDE4; --note-blue: #D6E8FA; }
body { background-image: radial-gradient(#E3E5E8 1px, transparent 1.1px); }
/* Labels: clean sans in marker red, no tilt. Handwriting stays only in the hero label and board lane titles */
.eyebrow { font: 600 13px/1.4 var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--brand-strong); transform: none; }
.hero .eyebrow { font-size: 13px; color: var(--fg-2); }
.board-note { font: 500 14px var(--sans); transform: none; margin: -24px 0 20px; }
.lane-head h3 { font-size: 26px; }
.note .go, .tldr dt { font-family: var(--sans); }
.note .go { font-size: 14px; font-weight: 600; }
.tldr dt { font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--fg-2); }
/* Gentler tilts and softer shadows */
.metric:nth-child(1), .pillars:not(.six) .pillar:nth-child(1), .tldr div:nth-child(1) { transform: rotate(-0.6deg); }
.metric:nth-child(2), .pillars:not(.six) .pillar:nth-child(2), .tldr div:nth-child(2) { transform: rotate(0.5deg); }
.metric:nth-child(3), .pillars:not(.six) .pillar:nth-child(3), .tldr div:nth-child(3) { transform: rotate(-0.4deg); }
.metric:nth-child(4) { transform: rotate(0.6deg); }
.board .lane .tile.note:nth-of-type(odd) { transform: rotate(-0.6deg); }
.board .lane .tile.note:nth-of-type(even) { transform: rotate(0.5deg); }
.metric, .pillars:not(.six) .pillar, .tldr div, .board .tile.note { box-shadow: 0 6px 14px -8px rgba(29,29,27,.28); border-radius: 6px; }
.board .tile.note:hover { box-shadow: 0 12px 20px -10px rgba(29,29,27,.32); transform: rotate(0) translateY(-3px); }
/* Tape only on the profile card */
.case.pinned::before, .contact-card.pinned::before { display: none; }
.cols > .part:only-child { grid-column: 1 / -1; }
.board .tile.note { padding-top: 18px; }
/* Calmer containers */
.case-head { background: none; }
.contact-card { background: var(--bg); border: 1px solid var(--line); border-radius: 20px; transform: none; box-shadow: 0 16px 30px -18px rgba(29,29,27,.25); }
.contact-card .sub { color: var(--fg-2); }
.contact-card .citem { background: var(--bg-2); box-shadow: none; }
.profile .cover { background: var(--note-yellow); }
"""

JS = SRC[SRC.index("<script>") + 8:SRC.index("</script>")]


def js_replace(old, new):
    global JS
    assert JS.count(old) == 1, old[:80]
    JS = JS.replace(old, new)


def js_wrap(start_comment, end_comment, guard):
    global JS
    i = JS.index(start_comment)
    j = JS.index(end_comment)
    JS = JS[:i] + "if (" + guard + ") {\n  " + JS[i:j].rstrip() + "\n  }\n\n  " + JS[j:]


# No theme toggle any more: one light look.
i = JS.index("  /* Theme */"); j = JS.index("  /* Work filter */")
JS = JS[:i] + JS[j:]
# Remember the chosen theme between pages (kept harmless if the button is absent).
if False: js_replace('root.setAttribute("data-theme", cur === "dark" ? "light" : "dark");',
           'var next = cur === "dark" ? "light" : "dark"; root.setAttribute("data-theme", next);\n'
           '    try { localStorage.setItem("theme", next); } catch (e) {}')
# Work filter: the demo filter sends visitors straight to the demo tab.
js_replace('$$("#tiles .tile").forEach(function (t) { t.hidden = !(f === "all" || t.dataset.group.split(" ").indexOf(f) > -1); });',
           '$$("#tiles .tile").forEach(function (t) {\n'
           '        t.hidden = !(f === "all" || t.dataset.group.split(" ").indexOf(f) > -1);\n'
           '        t.setAttribute("href", t.dataset.href + (f === "demo" ? "#demo" : ""));\n'
           '      });')
# Old single page behaviour that no longer applies.
i = JS.index("  // Tiles marked with a demo open the demo tab")
j = JS.index("  /* Copy */")
JS = JS[:i] + """  // Open a tab named in the address, e.g. work/preppo.html#demo
  var hashTab = location.hash.slice(1);
  if (hashTab) $$("[data-tabs]").forEach(function (card) { if ($('[data-tab="' + hashTab + '"]', card)) selectTab(card, hashTab); });

""" + JS[j:]
js_replace('  function flash(el) { el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); }\n', "")
js_replace('  $$("#tiles .tile").forEach(function (t) { t.addEventListener("click", function () { var c = $(t.getAttribute("href")); if (c) flash(c); }); });\n', "")
js_replace('    if (el.classList.contains("case")) flash(el);\n', "")
# Only section links on the current page take part in scroll highlighting.
js_replace('var navLinks = $$(".nav a"), secs',
           'var navLinks = $$(".nav a").filter(function (a) { return a.getAttribute("href").charAt(0) === "#"; }), secs')
# Demos only exist on their own pages.
js_wrap("/* Contract demo */", "/* Backlog demo */", '$("#cRun")')
js_wrap("/* Backlog demo */", "/* PrepPO demo */", '$("#rank")')
js_wrap("/* PrepPO demo */", "/* Scroll progress", '$("#chat")')
# Work dropdown and phone menu.
NAV_JS = """
  /* Work dropdown */
  var dd = $("#workDd");
  if (dd) {
    var ddBtn = $(".dd-btn", dd), ddMenu = $("#workMenu"), ddTimer;
    var hoverable = window.matchMedia && matchMedia("(hover: hover)").matches;
    function setDd(open) { ddMenu.hidden = !open; ddBtn.setAttribute("aria-expanded", open ? "true" : "false"); }
    ddBtn.addEventListener("click", function () { setDd(hoverable ? true : ddMenu.hidden); });
    if (hoverable) {
      dd.addEventListener("mouseenter", function () { clearTimeout(ddTimer); setDd(true); });
      dd.addEventListener("mouseleave", function () { ddTimer = setTimeout(function () { setDd(false); }, 160); });
    }
    document.addEventListener("click", function (e) { if (!dd.contains(e.target)) setDd(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !ddMenu.hidden) { setDd(false); ddBtn.focus(); } });
    $$("a", ddMenu).forEach(function (a) { a.addEventListener("click", function () { setDd(false); }); });
  }

  /* Board lane counts follow the work filter */
  var board = $(".board");
  if (board) $$(".filters button").forEach(function (b) {
    b.addEventListener("click", function () {
      setTimeout(function () { $$(".lane", board).forEach(function (l) { $(".count", l).textContent = $$(".tile:not([hidden])", l).length; }); }, 0);
    });
  });

  /* Phone menu */
  var menuBtn = $("#menuBtn"), mobileMenu = $("#mobileMenu");
  if (menuBtn && mobileMenu) {
    function setMenu(open) {
      mobileMenu.hidden = !open;
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      $("use", menuBtn).setAttribute("href", open ? "#i-close" : "#i-menu");
    }
    menuBtn.addEventListener("click", function () { setMenu(mobileMenu.hidden); });
    $$("a", mobileMenu).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !mobileMenu.hidden) setMenu(false); });
    window.addEventListener("resize", function () { if (innerWidth > 1024) setMenu(false); });
  }
"""
JS = JS.rstrip()
assert JS.endswith("})();")
JS = JS[:-5] + NAV_JS + "})();"

# Search palette: page links instead of in page anchors.
i = JS.index("  var ITEMS = [")
j = JS.index("];", i) + 2
items = ['    { l: "%s", g: "%s", page: "work/%s.html" }' % (t["title"], "Personal" if cid in ("preppo", "tamil") else "Efficio", SLUG[cid])
         for cid, t in tile_info().items()]
items += [
    '    { l: "Contract analysis simple demo", g: "Demo", page: "work/contract-analysis.html", tab: "demo" }',
    '    { l: "Backlog ranking simple demo", g: "Demo", page: "work/backlog-hub.html", tab: "demo" }',
    '    { l: "PrepPO simple demo", g: "Demo", page: "work/preppo.html", tab: "demo" }',
    '    { l: "Open PrepPO live", g: "Link", url: "https://prep-po.vercel.app" }',
    '    { l: "All work", g: "Page", page: "index.html", tab: "work" }',
    '    { l: "About and how I work", g: "Page", page: "about.html" }',
    '    { l: "Contact details", g: "Section", h: "#contact" }',
    '    { l: "Copy email address", g: "Action", act: "email" }',
    '    { l: "Open LinkedIn profile", g: "Link", url: "https://www.linkedin.com/in/ajanthsrik/" }'
]
JS = JS[:i] + "  var ROOT = document.body.getAttribute(\"data-root\") || \"\";\n  var ITEMS = [\n" + ",\n".join(items) + "\n  ];" + JS[j:]
js_replace('    if (x.act === "theme") { $("#themeBtn").click(); return; }',
           '    if (x.page) { location.href = ROOT + x.page + (x.tab ? "#" + x.tab : ""); return; }\n'
           '    if (x.act === "theme") { $("#themeBtn").click(); return; }')

SPRITE = block('<svg width="0" height="0"', "</svg>")
CONTACT = section_by_id("contact").replace('<div class="contact-card">', '<div class="contact-card pinned">')
TAIL = SRC[SRC.index("<footer>"):SRC.index("<script>")]
HEAD_LINKS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap">"""
FAVICON = re.search(r'<link rel="icon"[^>]*>', SRC).group(0).replace("fill='%237F56D9'", "fill='%23FFE27A'").replace("fill='white'", "fill='%231D1D1B'")


PERSONAL = {"preppo", "tamil"}
NAV_SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-chev" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></symbol>
  <symbol id="i-menu" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></symbol>
</svg>"""


def tool_links(root, current_cid, compact=False):
    """Menu items for every tool, grouped by where it was built."""
    out = {}
    for group in ("At Efficio", "Personal"):
        rows = []
        for cid, slug, _ in TOOLS:
            if (cid in PERSONAL) != (group == "Personal"):
                continue
            t = INFO[cid]
            cur = ' aria-current="page"' if cid == current_cid else ""
            if compact:
                rows.append(f'<a class="m-tool" href="{root}work/{slug}.html"{cur}><svg class="i"><use href="#{t["icon"]}"/></svg>{t["title"]}</a>')
            else:
                rows.append(f'<a class="dd-item" href="{root}work/{slug}.html"{cur}><span class="icon-tile"><svg class="i"><use href="#{t["icon"]}"/></svg></span>'
                            f'<span><b>{t["title"]}</b><small>{t["result"]}</small></span></a>')
        out[group] = "\n".join(rows)
    return out


def shell(root, title, desc, body, current=None, tool=None):
    on = lambda key: ' class="current"' if current == key else ""
    work_href = "#work" if current == "home" else root + "index.html#work"
    dd = tool_links(root, tool)
    mm = tool_links(root, tool, compact=True)
    header = f"""<header class="topbar">
  <div class="container">
    <a class="brand" href="{root}index.html"><span class="logo">AS</span><span>Ajanth Sri</span></a>
    <nav class="nav" aria-label="Main">
      <div class="dd" id="workDd">
        <button class="dd-btn{' current' if current == 'work' else ''}" type="button" aria-expanded="false" aria-controls="workMenu">Work<svg class="i"><use href="#i-chev"/></svg></button>
        <div class="dd-menu" id="workMenu" hidden>
          <div class="dd-col"><p class="dd-h">At Efficio</p>{dd["At Efficio"]}</div>
          <div class="dd-col"><p class="dd-h">Personal</p>{dd["Personal"]}
            <a class="dd-all" href="{work_href}">See all seven tools<svg class="i"><use href="#i-arrow"/></svg></a>
          </div>
        </div>
      </div>
      <a href="{root}about.html"{on('about')}>About</a>
      <a href="#contact">Contact</a>
    </nav>
    <div class="spacer"></div>
    <button class="search" type="button" id="openPalette" aria-label="Search the portfolio"><svg class="i"><use href="#i-search"/></svg><span>Jump to a tool</span><kbd>⌘K</kbd></button>
    <a class="btn primary cv" href="#contact">Get in touch</a>
    <button class="btn icon menu-btn" type="button" id="menuBtn" aria-expanded="false" aria-controls="mobileMenu" aria-label="Open menu"><svg class="i"><use href="#i-menu"/></svg></button>
  </div>
  <div class="mobile-menu" id="mobileMenu" hidden>
    <div class="container">
      <p class="dd-h">Work at Efficio</p>
      <div class="m-grid">{mm["At Efficio"]}</div>
      <p class="dd-h">Personal</p>
      <div class="m-grid">{mm["Personal"]}</div>
      <div class="m-links">
        <a href="{work_href}">All work</a>
        <a href="{root}about.html"{on('about')}>About and how I work</a>
        <a href="#contact">Contact</a>
      </div>
      <a class="btn primary m-cta" href="#contact">Get in touch</a>
    </div>
  </div>
</header>"""
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#FAFAF8">
{FAVICON}
{HEAD_LINKS}
<link rel="stylesheet" href="{root}assets/site.css">
<script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};
if (/vercel\\.app$/.test(location.hostname)) {{ var va = document.createElement("script"); va.defer = true; va.src = "/_vercel/insights/script.js"; document.head.appendChild(va); }}</script>
</head>
<body data-root="{root}">
{SPRITE}
{NAV_SPRITE}
<div class="scrollbar" aria-hidden="true"><div id="scrollFill"></div></div>
{header}
{body}
{TAIL}<script src="{root}assets/site.js"></script>
</body>
</html>
"""


def relink(html, root):
    """Point in page tool anchors at the tool pages."""
    for cid, slug, _ in TOOLS:
        html = html.replace(f'href="#{cid}"', f'href="{root}work/{slug}.html"')
    return html


# ---------- Home ----------
INFO = tile_info()
hero = block('<section class="hero">', "</section>")
hero = hero.replace('<span class="grad">builds the product.</span>',
                    '<span class="grad scribble-wrap">builds the product.<svg class="scribble" viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true">'
                    '<path d="M3 17 C 70 6, 160 4, 297 12 M 40 21 C 110 14, 200 13, 270 17"/></svg></span>')
hero = hero.replace('<aside class="profile"', '<aside class="profile pinned"')
metrics = SRC[SRC.index('<div class="container">\n    <div class="metrics">'):SRC.index('<section class="section" id="bring"')].rstrip()
work = section_by_id("work")
for cid, slug, demo in TOOLS:
    work = work.replace(f'<a class="tile" href="#{cid}"', f'<a class="tile" href="work/{slug}.html" data-href="work/{slug}.html"')
    work = work.replace(f'<a class="tile wide" href="#{cid}"', f'<a class="tile wide" href="work/{slug}.html" data-href="work/{slug}.html"')
assert 'href="#' not in re.sub(r'href="#i-', "", work), "a tile still points at an in page anchor"

# The work section stays a grid of cards (the board layout was dropped).


arrow = '<li class="arrow" aria-hidden="true"><svg class="i"><use href="#i-arrow"/></svg></li>'
stage = lambda icon, label: f'<li><span class="icon-tile"><svg class="i"><use href="#{icon}"/></svg></span>{label}</li>'
teaser = f"""<section class="section alt" id="approach">
    <div class="container">
      <div class="head">
        <p class="eyebrow">How I work</p>
        <h2>How I take a feature from idea to live</h2>
        <p class="sub">The process I follow for every feature.</p>
      </div>
      <ol class="flowrow">
        {stage('i-file', 'Specify')}{arrow}{stage('i-pen', 'Prototype')}{arrow}{stage('i-users', 'Test')}{arrow}{stage('i-rocket', 'Build')}
      </ol>
      <a class="btn" href="about.html">More about how I work <svg class="i"><use href="#i-arrow"/></svg></a>
    </div>
  </section>"""
logos = block('<section class="stackband"', "</section>")
import json as _json
_L = _json.load(open(os.path.join(HERE, "src", "logos.json"), encoding="utf-8"))
def _logo_list(hidden):
    items = "".join(
        f'<li class="lg{n}"><span class="lg"' + ("" if hidden else f' role="img" aria-label="{l["name"]} logo"') + f'></span><span>{l["name"]}</span></li>'
        for n, l in enumerate(_L))
    return ('<ul aria-hidden="true">' if hidden else "<ul>") + items + "</ul>"
logos = re.sub(r'<div class="track">.*?</div></div>', lambda m: '<div class="track">' + _logo_list(False) + _logo_list(True) + "</div></div>", logos, count=1, flags=re.S)
assert logos.count('class="lg"') == 2 * len(_L)
CSS += "\n" + "\n".join(f'.lg{n} {{ --c: {l["hex"]}; }} .lg{n} .lg {{ --m: url({l["mask"]}); width: {round(20 * l["ratio"])}px; }}' for n, l in enumerate(_L)) + "\n"

home_body = f"""<main id="top">
  {hero}

  {metrics}

  {work}

  {teaser}

  {logos}

  {CONTACT}
</main>"""
home = shell("", f"{NAME} | Product Owner",
             "Product Owner in London who builds the product. Seven tools, how they work and what they changed.",
             home_body, current="home")

# ---------- About ----------
bring = section_by_id("bring").replace(' style="padding-top:24px"', "")
platform = section_by_id("platform")
approach = section_by_id("approach").replace('<section class="section" id="approach">', '<section class="section" id="approach-full">')
about_body = f"""<main id="top">
  <section class="pagehead">
    <div class="container">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><span>About</span></nav>
      <h1>About me and how I work</h1>
      <p class="sub">What I bring, where I work and the principles behind my product calls.</p>
    </div>
  </section>

  {relink(bring, "")}

  {relink(platform, "")}

  {relink(approach, "")}

  {CONTACT}
</main>"""
about = shell("", f"About | {NAME}",
              "What I bring, where I work, and how I make product calls.",
              about_body, current="about")

# ---------- Tool pages ----------
pages = {"index.html": home, "about.html": about}
for n, (cid, slug, demo) in enumerate(TOOLS):
    art = article(cid)
    art = art.replace("<h3>", "<h1>", 1).replace("</h3>", "</h1>", 1).replace('<article class="case"', '<article class="case pinned"', 1)
    prev_cid, prev_slug, _ = TOOLS[n - 1]
    next_cid, next_slug, _ = TOOLS[(n + 1) % len(TOOLS)]
    t = INFO[cid]
    switch = "".join(
        f'<a class="sw" href="{s2}.html"' + (' aria-current="page"' if c2 == cid else "") + f'><svg class="i"><use href="#{INFO[c2]["icon"]}"/></svg>{INFO[c2]["title"]}</a>'
        for c2, s2, _ in TOOLS)
    pn = f"""<div class="pn">
        <a class="prev" href="{prev_slug}.html"><span class="k"><svg class="i"><use href="#i-arrow"/></svg>Previous tool</span><h3>{INFO[prev_cid]['title']}</h3><p>{INFO[prev_cid]['result']}</p></a>
        <a class="next" href="{next_slug}.html"><span class="k">Next tool<svg class="i"><use href="#i-arrow"/></svg></span><h3>{INFO[next_cid]['title']}</h3><p>{INFO[next_cid]['result']}</p></a>
      </div>
      <a class="backall" href="../index.html#work"><svg class="i"><use href="#i-arrow"/></svg>Back to all work</a>"""
    body = f"""<main id="top">
  <section class="case-page">
    <div class="container">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../index.html#work">Work</a><span>/</span><span>{t['title']}</span></nav>
      <nav class="switcher" aria-label="All tools">{switch}</nav>
      {relink(art, '../work/'.replace('work/', '')).replace('href="../work/', 'href="')}
      {pn}
    </div>
  </section>

  {CONTACT}
</main>"""
    pages[f"work/{slug}.html"] = shell("../", f"{t['title']} | {NAME}", summary_text(art), body, current="work", tool=cid)

# ---------- Write ----------
os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
# ---------- Remove style rules for parts of the page that no longer exist ----------
DEAD = {".pill", ".pill .badge", ".pulse", ".pulse::after", ".track li.mark img", ".stackband .track li.mark img",
        ".note-y", ".note-m", ".note-p", ".note-b", ".board-note", ".lane-head h3", ".note .go",
        ".board .lane .tile.note:nth-of-type(odd)", ".board .lane .tile.note:nth-of-type(even)",
        ".board .tile.note", ".board .tile.note:hover", ".board .tile.note::before", ".lane"}
def _prune(css):
    def fix(m):
        notes = "".join(re.findall(r"/\*.*?\*/", m.group(1), re.S))
        sels = [x.strip() for x in re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S).split(",")]
        keep = [x for x in sels if x not in DEAD]
        if not keep:
            return notes
        return (notes + "\n" if notes else "") + ", ".join(keep) + " {" + m.group(2) + "}"
    return re.sub(r"(?<![@\w-])([.#:\[\w][^{}@;]*?)\s*\{([^{}]*)\}", fix, css)
CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
CSS = re.sub(r"\n\s*\n+", "\n", CSS)
CSS = _prune(CSS)

# ---------- Motion: subtle, once, and off when Reduce Motion is on ----------
CSS += r"""
/* Hero entrance on load */
@media (prefers-reduced-motion: no-preference) {
  .hero .eyebrow, .hero h1, .hero .lede, .hero .actions, .hero .profile { animation: rise .7s cubic-bezier(.2,.7,.2,1) both; }
  .hero h1 { animation-delay: .08s; }
  .hero .lede { animation-delay: .16s; }
  .hero .actions { animation-delay: .24s; }
  .hero .profile { animation-delay: .3s; }
  .pagehead h1, .pagehead .sub, .case-page .crumbs, .case-page .switcher, .case-page .case { animation: rise .6s cubic-bezier(.2,.7,.2,1) both; }
  .pagehead .sub, .case-page .switcher { animation-delay: .08s; }
  .case-page .case { animation-delay: .14s; }
}
@keyframes rise { from { opacity: 0; translate: 0 14px; } to { opacity: 1; translate: 0 0; } }

/* Sections and cards ease in as they scroll into view */
.rv { opacity: 0; translate: 0 18px; transition: opacity .6s ease, translate .6s cubic-bezier(.2,.7,.2,1); }
.rv.in { opacity: 1; translate: 0 0; }

/* Process steps: a highlight travels Specify, Prototype, Test, Build */
.flowrow li .icon-tile { transition: background .35s, color .35s, transform .35s; }
.flowrow li.on .icon-tile { background: var(--brand); color: #fff; transform: scale(1.08); }
.flowrow li.arrow { transition: color .35s, transform .35s; }
.flowrow li.arrow.on { color: var(--brand); transform: translateX(3px); }
"""

ANIM_JS = """
  /* ---------- Motion ---------- */
  if (!reduce) {
    // Count up the headline figures when they come into view.
    var nums = $$(".metric .num, .kpi .num").filter(function (el) {
      return (el.textContent.match(/\\d[\\d,]*(\\.\\d+)?/g) || []).length === 1;
    });
    function countUp(el) {
      var full = el.textContent, m = full.match(/^(.*?)(\\d[\\d,]*(?:\\.\\d+)?)(.*)$/);
      if (!m) return;
      var target = parseFloat(m[2].replace(/,/g, "")), dec = (m[2].split(".")[1] || "").length, comma = m[2].indexOf(",") > -1;
      var t0 = performance.now(), dur = 1100;
      (function tick(t) {
        var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3), v = target * e;
        var txt = dec ? v.toFixed(dec) : String(Math.round(v));
        if (comma) txt = Number(txt).toLocaleString("en-GB", { minimumFractionDigits: dec, maximumFractionDigits: dec });
        el.textContent = k < 1 ? m[1] + txt + m[3] : full;
        if (k < 1) requestAnimationFrame(tick);
      })(t0);
    }

    // Ease in sections and cards that start below the fold.
    var cand = $$(".section .head, #tiles .tile, .pillar, .metric, .flowrow, .stackband, .contact-card, .scope, .pwins .metric, .steps li, .tldr div, .kpi, .pn a, .backall");
    var fold = window.innerHeight;
    cand.forEach(function (el) {
      if (el.getBoundingClientRect().top > fold * 0.92) {
        var sibs = Array.prototype.indexOf.call(el.parentNode.children, el);
        el.style.transitionDelay = Math.min(sibs, 5) * 70 + "ms";
        el.classList.add("rv");
      }
    });

    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var el = en.target;
          if (el.classList.contains("rv")) el.classList.add("in");
          if (el.classList.contains("num")) countUp(el);
          io.unobserve(el);
        });
      }, { threshold: 0.15, rootMargin: "0px 0px -6% 0px" });
      $$(".rv").forEach(function (el) { io.observe(el); });
      nums.forEach(function (el) { io.observe(el); });
    } else {
      $$(".rv").forEach(function (el) { el.classList.add("in"); });
    }
    // Safety: never leave anything hidden.
    setTimeout(function () { $$(".rv:not(.in)").forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add("in"); }); }, 2500);

    // Process steps highlight on the home page.
    var flow = $(".flowrow");
    if (flow) {
      var steps = $$("li", flow), si = 0;
      setInterval(function () {
        if (document.hidden) return;
        steps.forEach(function (li) { li.classList.remove("on"); });
        steps[si].classList.add("on");
        if (steps[si + 1] && steps[si + 1].classList.contains("arrow")) steps[si + 1].classList.add("on");
        si = (si + 2) % steps.length;
      }, 1300);
    }
  }
"""
JS = JS.rstrip()
assert JS.endswith("})();")
JS = JS[:-5] + ANIM_JS + "})();"

open(os.path.join(HERE, "assets", "site.css"), "w", encoding="utf-8").write(CSS.strip() + "\n")
open(os.path.join(HERE, "assets", "site.js"), "w", encoding="utf-8").write(JS.strip() + "\n")
for path, html in pages.items():
    open(os.path.join(HERE, path), "w", encoding="utf-8").write(html)
open(os.path.join(HERE, "vercel.json"), "w").write('{\n  "cleanUrls": true\n}\n')
print("built", len(pages), "pages")
