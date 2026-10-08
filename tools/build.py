#!/usr/bin/env python3
"""Build the Yan Group website into docs/ (served by GitHub Pages).

    python3 tools/build.py            # build
    python3 tools/build.py --serve    # build, then preview at http://localhost:8000

Content lives in data/*.json, content/*.md and data/publications.bib (copied from the twin's verified
bibliography). Markdown is converted with pandoc. No other dependencies.
"""
import html, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
D = lambda name: json.loads((ROOT / "data" / name).read_text())
SITE = "Yan Group"
TAGLINE = "AI and data-driven design of quantum and energy materials"
NAV = [("index.html", "Home"), ("research.html", "Research"), ("people.html", "People"),
       ("publications.html", "Publications"), ("code.html", "Code"), ("resources.html", "Resources"), ("news.html", "News"),
       ("teaching.html", "Teaching"), ("join.html", "Join")]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def md(path_or_text, is_text=False):
    src = path_or_text if is_text else Path(path_or_text).read_text()
    return subprocess.run(["pandoc", "-f", "markdown", "-t", "html5", "--wrap=none"], input=src,
                          capture_output=True, text=True, check=True).stdout


def page(fname, title, body, desc=""):
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{t}</a>' for h, t in NAV)
    full_title = f"{title} | {SITE} at Northeastern" if fname != "index.html" else f"{SITE}: {TAGLINE} | Northeastern University"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc or TAGLINE)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html"><span class="brand-name">{SITE}</span><span class="brand-sub">Northeastern University</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">☰</button>
    <nav id="site-nav" class="site-nav">{nav}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div><strong>Yan Group</strong> · Department of Physics, Northeastern University<br>Boston, MA 02115, USA</div>
    <div class="footer-links"><a href="mailto:q.yan@northeastern.edu">q.yan@northeastern.edu</a>
      <a href="https://github.com/qmatyanlab">GitHub</a>
      <a href="https://scholar.google.com/citations?user=ysfTfdkAAAAJ">Google Scholar</a>
      <a href="https://orcid.org/0000-0002-3377-0314">ORCID</a></div>
  </div>
</footer>
<script>
document.querySelector('.nav-toggle').addEventListener('click', e => {{
  const open = document.body.classList.toggle('nav-open'); e.currentTarget.setAttribute('aria-expanded', open);
}});
</script>
</body>
</html>
"""


def fmt_date(d):
    m = re.match(r"(\d{4})-(\d{2})", d)
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else d[:4]


# ---------- publications ----------
def parse_bib(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.S):
        typ, key, body = m.groups()
        f = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", body, re.S):
            f[fm.group(1).lower()] = re.sub(r"\s+", " ", fm.group(2)).strip()
        f["_type"], f["_key"] = typ.lower(), key
        entries.append(f)
    return entries


def tex2html(s):
    s = re.sub(r"\$_\{?([^}$]+)\}?\$", r"<sub>\1</sub>", s)
    s = re.sub(r"\$\^\{?([^}$]+)\}?\$", r"<sup>\1</sup>", s)
    s = s.replace("{", "").replace("}", "").replace("\\&", "&amp;").replace("--", "–").replace("\\", "")
    return s


def short_authors(a):
    names = [n.strip() for n in a.split(" and ") if n.strip()]
    out = []
    for n in names:
        n = tex2html(n)
        if "," in n:
            last, _, first = n.partition(",")
        else:
            parts = n.split()
            last, first = parts[-1], " ".join(parts[:-1])
        def ini(part):  # "Ting-Wei" -> "T.-W.", "J." -> "J."
            return "-".join(x[0] + "." for x in part.split("-") if x and x[0].isalpha())
        initials = " ".join(ini(p) for p in first.split())
        nm = f"{initials} {last.strip()}".strip()
        is_me = last.strip() == "Yan" and first.strip()[:1] == "Q"
        out.append(f"<strong>{nm}</strong>" if is_me else nm)
    return ", ".join(out)


def publications():
    bib = parse_bib((ROOT / "data/publications.bib").read_text())
    items = []
    for e in bib:
        if e.get("cv_number", "").startswith("P") or e["_type"] in ("patent",):
            continue
        venue = e.get("journal") or e.get("booktitle") or e.get("publisher") or ""
        if e["_type"] == "misc" and e.get("eprint"):
            venue = f"arXiv:{e['eprint']}"
        vol = f" <b>{e['volume']}</b>" if e.get("volume") else ""
        pages = f", {e['pages']}" if e.get("pages") else ""
        url = f"https://doi.org/{e['doi']}" if e.get("doi") else (f"https://arxiv.org/abs/{e['eprint']}" if e.get("eprint") else "")
        items.append({"year": e.get("year", ""), "n": int(re.sub(r"\D", "", e.get("cv_number", "0")) or 0),
                      "html": f"{short_authors(e.get('author', ''))}, “{tex2html(e.get('title', ''))},” "
                              f"<i>{tex2html(venue)}</i>{vol}{pages} ({e.get('year', '')}).",
                      "url": url})
    for x in D("extra_pubs.json"):
        a = x["authors"].replace("Q. Yan", "<strong>Q. Yan</strong>")
        items.append({"year": x["year"], "n": 999, "html": f"{a}, “{x['title']},” <i>{x['venue']}</i> ({x['year']}).", "url": x["url"]})
    items.sort(key=lambda i: (i["year"], i["n"]), reverse=True)
    body = ['<h1>Publications</h1>',
            '<p class="lede">Full list with citation metrics on <a href="https://scholar.google.com/citations?user=ysfTfdkAAAAJ">Google Scholar</a> '
            'and <a href="https://orcid.org/0000-0002-3377-0314">ORCID</a>. Preprints are listed under their arXiv year.</p>']
    year = None
    for i in items:
        if i["year"] != year:
            if year is not None:
                body.append("</ol>")
            year = i["year"]
            body.append(f'<h2 class="year">{year}</h2><ol class="pubs">')
        link = f' <a class="doi" href="{i["url"]}">link</a>' if i["url"] else ""
        body.append(f"<li>{i['html']}{link}</li>")
    body.append("</ol>")
    return "\n".join(body), len(items)


# ---------- pages ----------
def initials(name):
    return "".join(p[0] for p in name.replace("-", " ").split()[:2]).upper()


def person_card(p, alum=False):
    img = (f'<img src="assets/img/people/{p["photo"]}" alt="{html.escape(p["name"])}" loading="lazy">' if p.get("photo")
           else f'<div class="avatar" aria-hidden="true">{initials(p["name"])}</div>')
    role = p["role"] + (f" · since {p['since']}" if p.get("since") else "")
    now = f'<div class="now">Now: {html.escape(p["now"])}</div>' if alum and p.get("now") else ""
    return f'<div class="person">{img}<div><div class="pname">{html.escape(p["name"])}</div><div class="prole">{html.escape(role)}</div>{now}</div></div>'


def news_list(items, n=None):
    rows = items[:n] if n else items
    out = []
    for x in rows:
        link = f' <a href="{x["link"]}">→</a>' if x.get("link") else ""
        out.append(f'<li><time>{fmt_date(x["date"])}</time><span>{x["text"]}{link}</span></li>')
    return '<ul class="news">' + "".join(out) + "</ul>"


def research_cards(rhtml):
    secs = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>\s*<p>(.*?)</p>', rhtml, re.S)
    cards = []
    for sid, title, para in secs:
        t = re.sub(r"^\d+\.\s*", "", title)
        first = re.split(r"(?<=[.])\s", re.sub(r"<[^>]+>", "", para))[0]
        cards.append(f'<a class="card" href="research.html#{sid}"><h3>{t}</h3><p>{first}</p></a>')
    return '<div class="cards">' + "".join(cards) + "</div>"


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets/css", OUT / "assets/css")
    (OUT / "assets/img").mkdir()
    for p in (ROOT / "assets/img").iterdir():
        if p.name in ("wix",):
            continue
        if p.is_dir():
            shutil.copytree(p, OUT / "assets/img" / p.name, ignore=shutil.ignore_patterns("incoming", ".DS_Store"))
        else:
            shutil.copy(p, OUT / "assets/img" / p.name)
    people, news = D("people.json"), D("news.json")
    rhtml = md(ROOT / "content/research.md")
    rhtml = re.sub(r"<h1[^>]*>.*?</h1>", "", rhtml, count=1, flags=re.S)
    pi = people["pi"]

    home = f"""
<section class="hero">
  <div>
    <p class="eyebrow">Department of Physics · Northeastern University</p>
    <h1>{TAGLINE[0].upper() + TAGLINE[1:]}</h1>
    <p class="lede">We combine physics-informed machine learning, symmetry, and first-principles computation to understand and design
    quantum and functional materials, from equivariant neural networks and generative inverse design to quantum defects in
    two-dimensional materials.</p>
    <p class="cta"><a class="btn" href="research.html">Our research</a><a class="btn ghost" href="join.html">Join the group</a></p>
  </div>
  <figure class="pi">
    <img src="assets/img/people/{pi['photo']}" alt="Qimin Yan">
    <figcaption><strong>Qimin Yan</strong><br>{pi['title']}</figcaption>
  </figure>
</section>
<section><h2>Research directions</h2>{research_cards(rhtml)}</section>
<section class="two-col">
  <div><h2>News</h2>{news_list(news, 6)}<p><a href="news.html">All news →</a></p></div>
  <div><h2>About the PI</h2>{md((ROOT / 'content/bio.md'))}</div>
</section>"""
    (OUT / "index.html").write_text(page("index.html", "Home", home))

    (OUT / "research.html").write_text(page("research.html", "Research", '<h1>Research</h1><div class="prose research">' + rhtml + "</div>",
                                            "Research directions of the Yan Group"))

    cur = "".join(person_card(p) for p in people["current"])
    alum = "".join(person_card(p, alum=True) for p in people["alumni"])
    ppl = f"""<h1>People</h1>
<section class="pi-block">
  <img src="assets/img/people/{pi['photo']}" alt="Qimin Yan">
  <div><h2>Qimin Yan</h2><p class="prole">{pi['title']}, Department of Physics, Northeastern University</p>
  {md(ROOT / 'content/bio.md')}
  <p class="links"><a href="mailto:{pi['email']}">{pi['email']}</a> · <a href="{pi['scholar']}">Google Scholar</a> ·
  <a href="https://orcid.org/{pi['orcid']}">ORCID</a> · <a href="{pi['github']}">GitHub</a></p></div>
</section>
<h2>Group members</h2><div class="people">{cur}</div>
<h2>Alumni</h2><div class="people alumni">{alum}</div>
<figure class="group-photo"><img src="assets/img/group-2019.jpg" alt="Group photo, October 2019" loading="lazy"><figcaption>Group photo, October 2019.</figcaption></figure>"""
    (OUT / "people.html").write_text(page("people.html", "People", ppl))

    pubs, n = publications()
    (OUT / "publications.html").write_text(page("publications.html", "Publications", pubs))

    code = "".join(f"""<div class="repo"><h3><a href="{r['url']}">{r['name']}</a></h3><p>{r['desc']}</p>
<p class="paper">{f'Paper: <a href="{r["paper_url"]}">{r["paper"]}</a>' if r['paper'] else ''}</p></div>""" for r in D("code.json"))
    (OUT / "code.html").write_text(page("code.html", "Code", f"""<h1>Code and data</h1>
<p class="lede">Open-source software from the group, on <a href="https://github.com/qmatyanlab">GitHub</a>.</p><div class="repos">{code}</div>"""))

    (OUT / "news.html").write_text(page("news.html", "News", "<h1>News</h1>" + news_list(news)))
    for name, title in (("teaching", "Teaching"), ("join", "Join the group"), ("resources", "Resources")):
        (OUT / f"{name}.html").write_text(page(f"{name}.html", title, '<div class="prose">' + md(ROOT / f"content/{name}.md") + "</div>"))
    (OUT / "CNAME").write_text("www.qyanlab.net")
    (OUT / ".nojekyll").write_text("")
    print(f"built {OUT} ({n} publications, {len(news)} news items)")


if __name__ == "__main__":
    main()
    if "--serve" in sys.argv:
        subprocess.run([sys.executable, "-m", "http.server", "8000", "-d", str(OUT)])
