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


# Remember the chosen theme between pages.
js_replace('root.setAttribute("data-theme", cur === "dark" ? "light" : "dark");',
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
    '    { l: "Open LinkedIn profile", g: "Link", url: "https://www.linkedin.com/in/ajanthsrik/" }',
    '    { l: "Switch light or dark mode", g: "Action", act: "theme" }',
]
JS = JS[:i] + "  var ROOT = document.body.getAttribute(\"data-root\") || \"\";\n  var ITEMS = [\n" + ",\n".join(items) + "\n  ];" + JS[j:]
js_replace('    if (x.act === "theme") { $("#themeBtn").click(); return; }',
           '    if (x.page) { location.href = ROOT + x.page + (x.tab ? "#" + x.tab : ""); return; }\n'
           '    if (x.act === "theme") { $("#themeBtn").click(); return; }')

SPRITE = block('<svg width="0" height="0"', "</svg>")
CONTACT = section_by_id("contact")
TAIL = SRC[SRC.index("<footer>"):SRC.index("<script>")]
HEAD_LINKS = re.search(r'<link rel="preconnect".*?display=swap">', SRC, re.S).group(0)
FAVICON = re.search(r'<link rel="icon"[^>]*>', SRC).group(0)


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
    <button class="btn icon" type="button" id="themeBtn" aria-label="Switch light or dark mode"><svg class="i"><use href="#i-moon"/></svg></button>
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
<meta name="theme-color" content="#7F56D9">
{FAVICON}
{HEAD_LINKS}
<link rel="stylesheet" href="{root}assets/site.css">
<script>try {{ var t = localStorage.getItem("theme"); if (t) document.documentElement.setAttribute("data-theme", t); }} catch (e) {{}}</script>
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
metrics = SRC[SRC.index('<div class="container">\n    <div class="metrics">'):SRC.index('<section class="section" id="bring"')].rstrip()
work = section_by_id("work")
for cid, slug, demo in TOOLS:
    work = work.replace(f'<a class="tile" href="#{cid}"', f'<a class="tile" href="work/{slug}.html" data-href="work/{slug}.html"')
    work = work.replace(f'<a class="tile wide" href="#{cid}"', f'<a class="tile wide" href="work/{slug}.html" data-href="work/{slug}.html"')
assert 'href="#' not in re.sub(r'href="#i-', "", work), "a tile still points at an in page anchor"

arrow = '<li class="arrow" aria-hidden="true"><svg class="i"><use href="#i-arrow"/></svg></li>'
stage = lambda icon, label: f'<li><span class="icon-tile"><svg class="i"><use href="#{icon}"/></svg></span>{label}</li>'
teaser = f"""<section class="section alt" id="approach">
    <div class="container">
      <div class="head">
        <p class="eyebrow">How I work</p>
        <h2>How I take a feature from idea to live</h2>
        <p class="sub">The process I follow for every new feature, plus what I bring, where I work and how I make product calls.</p>
      </div>
      <ol class="flowrow">
        {stage('i-file', 'Specify')}{arrow}{stage('i-pen', 'Prototype')}{arrow}{stage('i-users', 'Test')}{arrow}{stage('i-rocket', 'Build')}
      </ol>
      <a class="btn" href="about.html">More about how I work <svg class="i"><use href="#i-arrow"/></svg></a>
    </div>
  </section>"""
logos = block('<section class="stackband"', "</section>")
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
      <p class="sub">What I bring, where I work, and the principles behind the product calls in each tool.</p>
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
    art = art.replace("<h3>", "<h1>", 1).replace("</h3>", "</h1>", 1)
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
open(os.path.join(HERE, "assets", "site.css"), "w", encoding="utf-8").write(CSS.strip() + "\n")
open(os.path.join(HERE, "assets", "site.js"), "w", encoding="utf-8").write(JS.strip() + "\n")
for path, html in pages.items():
    open(os.path.join(HERE, path), "w", encoding="utf-8").write(html)
open(os.path.join(HERE, "vercel.json"), "w").write('{\n  "cleanUrls": true\n}\n')
print("built", len(pages), "pages")
