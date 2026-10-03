(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  /* Toast */
  var toastT;
  function toast(msg) { $("#toastMsg").textContent = msg; $("#toast").hidden = false; clearTimeout(toastT); toastT = setTimeout(function () { $("#toast").hidden = true; }, 1800); }

  /* Theme */
  $("#themeBtn").addEventListener("click", function () {
    var root = document.documentElement;
    var cur = root.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    var next = cur === "dark" ? "light" : "dark"; root.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
  });

  /* Work filter */
  $$(".filters button").forEach(function (b) {
    b.addEventListener("click", function () {
      $$(".filters button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var f = b.dataset.filter;
      $$("#tiles .tile").forEach(function (t) {
        t.hidden = !(f === "all" || t.dataset.group.split(" ").indexOf(f) > -1);
        t.setAttribute("href", t.dataset.href + (f === "demo" ? "#demo" : ""));
      });
    });
  });

  /* Case tabs */
  function selectTab(card, name) {
    $$(".tabbar button", card).forEach(function (b) { b.setAttribute("aria-selected", b.dataset.tab === name ? "true" : "false"); });
    $$(".panel", card).forEach(function (p) { var on = p.dataset.panel === name; p.hidden = !on; if (on) { p.classList.remove("fade"); void p.offsetWidth; p.classList.add("fade"); } });
  }
  $$("[data-tabs]").forEach(function (card) {
    $$(".tabbar button", card).forEach(function (b) { b.addEventListener("click", function () { selectTab(card, b.dataset.tab); }); });
  });
  // Open a tab named in the address, e.g. work/preppo.html#demo
  var hashTab = location.hash.slice(1);
  if (hashTab) $$("[data-tabs]").forEach(function (card) { if ($('[data-tab="' + hashTab + '"]', card)) selectTab(card, hashTab); });

  /* Copy */
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var el = document.getElementById(btn.dataset.copy), text = el.textContent.trim();
      function fallback() { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); toast("Selected. Press Ctrl C to copy"); }
      try { navigator.clipboard.writeText(text).then(function () { toast("Copied to clipboard"); }, fallback); } catch (e) { fallback(); }
    });
  });

  if ($("#cRun")) {
  /* Contract demo */
  var CLAUSES = [
    { c: "Payment terms", k: "45 days", p: "60 days", met: false },
    { c: "Liability cap", k: "150% of annual fees", p: "At least 100% of annual fees", met: true },
    { c: "Termination notice", k: "90 days", p: "30 days", met: false },
    { c: "Price increases", k: "Capped at inflation", p: "Capped at inflation", met: true },
    { c: "Governing law", k: "England and Wales", p: "England and Wales", met: true },
    { c: "Renewal", k: "Renews automatically for 12 months", p: "No automatic renewal", met: false }
  ];
  var cState = "idle", agreed = {};
  function renderContract() {
    var rows = CLAUSES.map(function (x, i) {
      var res, act = "";
      if (cState !== "done") res = '<span class="badge">Waiting</span>';
      else if (x.met) res = '<span class="badge ok"><span class="dot"></span>Met</span>';
      else if (agreed[i]) res = '<span class="badge brand"><span class="dot"></span>Agreed deviation</span>';
      else { res = '<span class="badge bad"><span class="dot"></span>Not met</span>'; act = '<button class="linkbtn" type="button" data-agree="' + i + '">Mark as agreed</button>'; }
      if (cState === "done" && agreed[i]) act = '<button class="linkbtn" type="button" data-undo="' + i + '">Undo</button>';
      return "<tr><td class='clause'>" + x.c + "</td><td>" + x.k + "</td><td>" + x.p + "</td><td>" + res + "</td><td>" + act + "</td></tr>";
    }).join("");
    $("#cRows").innerHTML = rows;
    var s = $("#cSummary");
    if (cState === "done") {
      var met = CLAUSES.filter(function (x) { return x.met; }).length;
      var ag = Object.keys(agreed).length, open = CLAUSES.length - met - ag;
      s.innerHTML = '<span class="badge ok"><span class="dot"></span>' + met + ' met</span><span class="badge bad"><span class="dot"></span>' + open + ' not met</span>' + (ag ? '<span class="badge brand"><span class="dot"></span>' + ag + ' agreed</span>' : "") + "<span>" + (ag ? "Agreed deviations will not be flagged as risks on the next run." : "Mark a position the client has accepted as an agreed deviation.") + "</span>";
    } else if (cState === "idle") {
      s.innerHTML = '<span class="badge">Not analysed yet</span><span>Press Run analysis to check six clauses against the sample playbook.</span>';
    }
    $$("[data-agree]").forEach(function (b) { b.addEventListener("click", function () { agreed[b.dataset.agree] = true; renderContract(); toast("Saved as an agreed deviation"); }); });
    $$("[data-undo]").forEach(function (b) { b.addEventListener("click", function () { delete agreed[b.dataset.undo]; renderContract(); }); });
  }
  $("#cRun").addEventListener("click", function () {
    if (cState === "running") return;
    cState = "running"; agreed = {}; renderContract();
    $("#cSummary").innerHTML = '<span class="badge warn"><span class="dot"></span>Analysing</span><span>Sample supplier agreement</span>';
    $("#cRun").disabled = true; $("#cLog").hidden = false;
    var steps = ["Sending payload to the contract API", "Stored in S3, Lambda started", "Bedrock reviewing clause 1 of 6", "Bedrock reviewing clause 3 of 6", "Bedrock reviewing clause 6 of 6", "Results returned to Connected Platform"];
    var i = 0, gap = reduce ? 80 : 450;
    (function next() {
      if (i < steps.length) { $("#cStep").textContent = steps[i]; $("#cBar").style.width = Math.round(((i + 1) / steps.length) * 100) + "%"; i++; setTimeout(next, gap); }
      else { cState = "done"; $("#cRun").disabled = false; $("#cLog").hidden = true; $("#cBar").style.width = "0"; renderContract(); toast("Analysis complete"); }
    })();
  });
  $("#cReset").addEventListener("click", function () { cState = "idle"; agreed = {}; $("#cRun").disabled = false; $("#cLog").hidden = true; renderContract(); });
  renderContract();
  }

  if ($("#rank")) {
  /* Backlog demo */
  var TICKETS = [
    { id: "CP-412", t: "Export reports straight to PowerPoint", type: "Feature", m: "Must", ci: 5, ra: 3 },
    { id: "CP-388", t: "Bulk upload of supplier lists", type: "Feature", m: "Should", ci: 4, ra: 5 },
    { id: "CP-401", t: "Save dashboard filter presets", type: "Feature", m: "Should", ci: 3, ra: 2 },
    { id: "CP-375", t: "Single sign on for client users", type: "Feature", m: "Must", ci: 4, ra: 4 },
    { id: "CP-420", t: "Dark mode for the savings summary", type: "Feature", m: "Could", ci: 1, ra: 1 },
    { id: "CP-366", t: "Scheduled email digests", type: "Feature", m: "Could", ci: 2, ra: 4 },
    { id: "CP-409", t: "Faster loading on the initiatives page", type: "Feature", m: "Should", ci: 4, ra: 3 },
    { id: "CP-352", t: "Category benchmarking view", type: "Feature", m: "Should", ci: 3, ra: 5 }
  ];
  var MBASE = { Must: 40, Should: 25, Could: 10, "Won't": 0 }, typeF = "all";
  function score(x, w) { return Math.round(MBASE[x.m] + (w * x.ci + (1 - w) * x.ra) * 12); }
  function renderRank(animate) {
    var w = $("#wImpact").value / 100;
    $("#wOut").textContent = Math.round(w * 100) + "% client impact · " + Math.round((1 - w) * 100) + "% roadmap";
    var list = $("#rank"), before = {};
    $$("li", list).forEach(function (li) { before[li.dataset.id] = li.getBoundingClientRect().top; });
    var items = TICKETS.filter(function (x) { return typeF === "all" || x.type === typeF; })
      .map(function (x) { return { x: x, s: score(x, w) }; })
      .sort(function (a, b) { return b.s - a.s; });
    var existing = {}; $$("li", list).forEach(function (li) { existing[li.dataset.id] = li; });
    list.innerHTML = "";
    items.forEach(function (o, i) {
      var li = existing[o.x.id] || document.createElement("li");
      li.dataset.id = o.x.id;
      var mClass = o.x.m === "Must" ? "bad" : o.x.m === "Should" ? "warn" : "";
      li.innerHTML = '<span class="pos">' + (i + 1) + '</span><div><p class="t">' + o.x.t + '</p><div class="m"><span class="badge">' + o.x.id + '</span><span class="badge ' + (o.x.type === "Bug" ? "bad" : "brand") + '">' + o.x.type + '</span><span class="badge ' + mClass + '">' + o.x.m + ' have</span></div></div><span class="score">' + o.s + "</span>";
      li.style.transition = "none"; li.style.transform = "";
      list.appendChild(li);
    });
    if (animate && !reduce) {
      $$("li", list).forEach(function (li) {
        var b = before[li.dataset.id]; if (b === undefined) return;
        var d = b - li.getBoundingClientRect().top; if (!d) return;
        li.style.transform = "translateY(" + d + "px)";
        requestAnimationFrame(function () { requestAnimationFrame(function () { li.style.transition = "transform .35s ease"; li.style.transform = ""; }); });
      });
    }
  }
  $("#wImpact").addEventListener("input", function () { renderRank(true); });
  $$(".weights .seg button").forEach(function (b) {
    b.addEventListener("click", function () {
      $$(".weights .seg button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      typeF = b.dataset.type; renderRank(false);
    });
  });
  renderRank(false);
  }

  if ($("#chat")) {
  /* PrepPO demo */
  var ROUNDS = {
    talent: { turns: ["Your two minute career story, told as one clear thread towards this role.", "Why this company specifically.", "The one achievement on your CV most relevant to this role, with numbers.", "Notice period, salary expectations and start date.", "The questions you plan to ask the recruiter."],
      sheet: "Career narrative, genuine motivation, salary and notice preparation, screening questions with answers, and questions for the recruiter." },
    hm: { turns: ["Why your career moved the way it did, using the job titles on your CV.", "A project that matches the toughest requirement in the job description, with a measurable outcome.", "A time you pushed back on a stakeholder, and what happened.", "Your one or two biggest gaps against the job, and how you will handle them.", "Why this company, with something real about it."],
      sheet: "Three deep STAR stories, an honest gap analysis with exact wording, likely hiring manager questions, and smart questions to ask." },
    tech: { turns: ["Your confidence from 1 to 10 in each key tool in the job description, and the gaps.", "The frameworks you use day to day for prioritisation, discovery and delivery.", "How you would approach a specific problem from the job description.", "The most technically complex thing you have shipped, and your decisions.", "How you would approach a take home task."],
      sheet: "Tool confidence ratings, framework examples, structured answers, and likely technical questions." },
    final: { turns: ["Examples of you influencing product direction.", "A time you led without authority.", "A genuine professional failure and what changed afterwards.", "How your values connect to the company's values.", "Where you want to be in three to five years."],
      sheet: "Strategic thinking examples, leadership stories, values alignment, your growth story, and questions for senior leaders." }
  };
  var round = "hm", shown = 1;
  function msg(who, body, cls) {
    return '<div class="msg ' + (cls || "") + '"><span class="av">P</span><div><p class="meta"><b>PrepPO</b>' + who + '</p><div class="bubble">' + body + "</div></div></div>";
  }
  function renderChat() {
    var r = ROUNDS[round], html = "";
    for (var i = 0; i < shown && i < 5; i++) html += msg("Turn " + (i + 1) + " of 5", r.turns[i]);
    if (shown > 5) html += msg("Cheat sheet ready", "<b>Your sheet focuses on:</b> " + r.sheet, "sheet");
    $("#chat").innerHTML = html;
    $("#chatCount").textContent = shown > 5 ? "Cheat sheet ready" : "Turn " + shown + " of 5";
    $("#chatNext").textContent = shown > 5 ? "Start again" : shown === 5 ? "Build cheat sheet" : "Next turn";
    var last = $("#chat .msg:last-child"); if (last && !reduce) { last.classList.add("fade"); last.style.animation = "fade .3s ease"; }
  }
  $$("#rounds button").forEach(function (b) {
    b.addEventListener("click", function () {
      $$("#rounds button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      round = b.dataset.round; shown = 1; renderChat();
    });
  });
  $("#chatNext").addEventListener("click", function () { shown = shown > 5 ? 1 : shown + 1; renderChat(); });
  $("#chatAll").addEventListener("click", function () { shown = 6; renderChat(); });
  renderChat();
  }

  /* Scroll progress, active nav, back to top */
  var navLinks = $$(".nav a").filter(function (a) { return a.getAttribute("href").charAt(0) === "#"; }), secs = navLinks.map(function (a) { return document.querySelector(a.getAttribute("href")); });
  function onScroll() {
    var d = document.documentElement, max = d.scrollHeight - d.clientHeight;
    $("#scrollFill").style.width = (max > 0 ? (d.scrollTop / max) * 100 : 0) + "%";
    $("#toTop").hidden = d.scrollTop < 900;
    var cur = -1;
    secs.forEach(function (s, i) { if (s && s.getBoundingClientRect().top < 140) cur = i; });
    navLinks.forEach(function (a, i) { a.classList.toggle("active", i === cur); });
  }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  $("#toTop").addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  /* Command palette */
  var ROOT = document.body.getAttribute("data-root") || "";
  var ITEMS = [
    { l: "AI contract analysis", g: "Efficio", page: "work/contract-analysis.html" },
    { l: "Market Intelligence", g: "Efficio", page: "work/market-intelligence.html" },
    { l: "Backlog Prioritisation Hub", g: "Efficio", page: "work/backlog-hub.html" },
    { l: "Supplier Framework", g: "Efficio", page: "work/supplier-framework.html" },
    { l: "AI Product Owner Toolkit", g: "Efficio", page: "work/po-toolkit.html" },
    { l: "PrepPO", g: "Personal", page: "work/preppo.html" },
    { l: "Tamil learning app", g: "Personal", page: "work/tamil-app.html" },
    { l: "Contract analysis simple demo", g: "Demo", page: "work/contract-analysis.html", tab: "demo" },
    { l: "Backlog ranking simple demo", g: "Demo", page: "work/backlog-hub.html", tab: "demo" },
    { l: "PrepPO simple demo", g: "Demo", page: "work/preppo.html", tab: "demo" },
    { l: "Open PrepPO live", g: "Link", url: "https://prep-po.vercel.app" },
    { l: "All work", g: "Page", page: "index.html", tab: "work" },
    { l: "About and how I work", g: "Page", page: "about.html" },
    { l: "Contact details", g: "Section", h: "#contact" },
    { l: "Copy email address", g: "Action", act: "email" },
    { l: "Open LinkedIn profile", g: "Link", url: "https://www.linkedin.com/in/ajanthsrik/" },
    { l: "Switch light or dark mode", g: "Action", act: "theme" }
  ];
  var sel = 0, filtered = ITEMS;
  function openP() { $("#overlay").hidden = false; $("#pq").value = ""; filterP(); setTimeout(function () { $("#pq").focus(); }, 0); }
  function closeP() { $("#overlay").hidden = true; }
  function filterP() {
    var q = $("#pq").value.toLowerCase().trim();
    filtered = ITEMS.filter(function (x) { return !q || (x.l + " " + x.g).toLowerCase().indexOf(q) > -1; });
    sel = 0; drawP();
  }
  function drawP() {
    var ul = $("#plist");
    if (!filtered.length) { ul.innerHTML = '<p class="empty">Nothing matches. Try a tool name such as PrepPO.</p>'; return; }
    ul.innerHTML = filtered.map(function (x, i) { return '<li role="option" data-i="' + i + '" aria-selected="' + (i === sel) + '">' + x.l + '<span class="grp">' + x.g + "</span></li>"; }).join("");
    $$("li", ul).forEach(function (li) {
      li.addEventListener("click", function () { runP(filtered[+li.dataset.i]); });
      li.addEventListener("mousemove", function () { if (sel !== +li.dataset.i) { sel = +li.dataset.i; drawP(); } });
    });
    var cur = $("li[aria-selected='true']", ul); if (cur) cur.scrollIntoView({ block: "nearest" });
  }
  function runP(x) {
    closeP();
    if (x.url) { var a = document.createElement("a"); a.href = x.url; a.target = "_blank"; a.rel = "noopener"; a.click(); return; }
    if (x.page) { location.href = ROOT + x.page + (x.tab ? "#" + x.tab : ""); return; }
    if (x.act === "theme") { $("#themeBtn").click(); return; }
    if (x.act === "email") { $("[data-copy='email']").click(); return; }
    var el = $(x.h); if (!el) return;
    if (x.tab && el.hasAttribute("data-tabs")) selectTab(el, x.tab);
    el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }
  $("#openPalette").addEventListener("click", openP);
  $("#pq").addEventListener("input", filterP);
  $("#overlay").addEventListener("click", function (e) { if (e.target.id === "overlay") closeP(); });
  document.addEventListener("keydown", function (e) {
    var open = !$("#overlay").hidden;
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); open ? closeP() : openP(); return; }
    if (!open && e.key === "/" && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); openP(); return; }
    if (!open) return;
    if (e.key === "Escape") closeP();
    else if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(sel + 1, filtered.length - 1); drawP(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(sel - 1, 0); drawP(); }
    else if (e.key === "Enter" && filtered[sel]) { e.preventDefault(); runP(filtered[sel]); }
  });

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
})();
