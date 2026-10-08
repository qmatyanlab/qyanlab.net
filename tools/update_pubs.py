#!/usr/bin/env python3
"""Find Qimin Yan's new publications and add them to the site data (run monthly by GitHub Actions).

    python3 tools/update_pubs.py [--months 18] [--dry-run]

Sources: ORCID and OpenAlex (works linked to ORCID 0000-0002-3377-0314: reliable identity), arXiv
(au:Yan_Qimin; accepted only with a known co-author). Every added item is verified against Crossref
(journal papers) or the arXiv API (preprints). Nothing is guessed: incomplete or uncertain items are
reported under "Needs confirmation" and not added.

Writes data/publications.bib, data/extra_pubs.json, data/news.json, and build/pr_body.md; prints
"changed=true|false" (also to $GITHUB_OUTPUT).
"""
import argparse, datetime as dt, difflib, html, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ORCID = "0000-0002-3377-0314"
UA = {"User-Agent": "qyanlab.net-publication-check/1.0 (+https://www.qyanlab.net)"}
# group members (given, family): first-author papers by them get a "Congratulations" news item
GROUP = [("Zhenyao", "Fang"), ("Ting-Wei", "Hsu"), ("Anoj", "Aryal"), ("Alex", "Heilman"), ("Alexander", "Heilman"),
         ("Yu", "Ruan"), ("Weiyi", "Gong"), ("Yubo", "Qi"), ("Jeng-Yuan", "Tsai")]
FIRST_NAME = {"Alexander": "Alex"}
COLLAB = {"bansil", "kar", "ren", "jariwala", "li", "ling", "fang", "hsu", "aryal", "heilman", "ruan", "gong", "qi", "tsai",
          "chowdhury", "hu", "liu", "shih", "perdew", "ruzsinszky"}


def get(url, accept="application/json", tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={**UA, "Accept": accept})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # rate limits / transient errors
            if k == tries - 1:
                print(f"WARN {url}: {e}", file=sys.stderr)
                return None
            time.sleep(3 * (k + 1))


def norm(t):
    t = re.sub(r"<[^>]+>|\$[^$]*\$|[{}\\]", "", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def existing():
    bib = (ROOT / "data/publications.bib").read_text()
    dois = {d.lower() for d in re.findall(r"doi\s*=\s*\{([^}]+)\}", bib)}
    arx = set(re.findall(r"eprint\s*=\s*\{([^}]+)\}", bib)) | set(re.findall(r"arXiv[.:](\d{4}\.\d{4,5})", bib))
    titles = [norm(t) for t in re.findall(r"\btitle\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", bib)]
    extra = json.loads((ROOT / "data/extra_pubs.json").read_text())
    for x in extra:
        m = re.search(r"(\d{4}\.\d{4,5})", x.get("url", "") + x.get("venue", ""))
        if m:
            arx.add(m.group(1))
        titles.append(norm(x["title"]))
    return bib, dois, arx, titles, extra


def seen_title(t, titles):
    n = norm(t)
    return any(difflib.SequenceMatcher(None, n, x).ratio() > 0.92 for x in titles)


def orcid_ids():
    d = get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    dois, arx = set(), set()
    if not d:
        return dois, arx
    for g in json.loads(d).get("group", []):
        for e in (g.get("external-ids") or {}).get("external-id", []):
            v = (e.get("external-id-value") or "").strip()
            if e.get("external-id-type") == "doi":
                m = re.search(r"arxiv\.(\d{4}\.\d{4,5})", v, re.I)
                (arx.add(m.group(1)) if m else dois.add(v.lower()))
            elif e.get("external-id-type") == "arxiv":
                m = re.search(r"(\d{4}\.\d{4,5})", v)
                m and arx.add(m.group(1))
    return dois, arx


def openalex_ids(since):
    d = get(f"https://api.openalex.org/works?filter=author.orcid:{ORCID},from_publication_date:{since}&per-page=100")
    dois, arx = set(), set()
    if not d:
        return dois, arx
    for w in json.loads(d).get("results", []):
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        m = re.search(r"arxiv\.(\d{4}\.\d{4,5})", doi)
        if m:
            arx.add(m.group(1))
        elif doi:
            dois.add(doi)
    return dois, arx


def arxiv_search():
    x = get("https://export.arxiv.org/api/query?search_query=au:Yan_Qimin&sortBy=submittedDate&sortOrder=descending&max_results=40",
            accept="application/atom+xml")
    out = {}
    if not x:
        return out
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in ET.fromstring(x).findall("a:entry", ns):
        aid = re.search(r"(\d{4}\.\d{4,5})", e.find("a:id", ns).text).group(1)
        out[aid] = ([n.text for n in e.findall("a:author/a:name", ns)], e.find("a:published", ns).text[:10])
    return out


def arxiv_meta_batch(ids):
    """Metadata for many arXiv IDs in one request (arXiv throttles per-ID loops)."""
    out = {}
    if not ids:
        return out
    x = None
    for wait in (0, 15, 60, 180):
        time.sleep(wait)
        x = get(f"https://export.arxiv.org/api/query?id_list={','.join(sorted(ids))}&max_results={len(ids)}",
                accept="application/atom+xml", tries=1)
        if x:
            break
    if not x:
        return out
    ns = {"a": "http://www.w3.org/2005/Atom"}
    ax = "{http://arxiv.org/schemas/atom}"
    for e in ET.fromstring(x).findall("a:entry", ns):
        if e.find("a:title", ns) is None:
            continue
        aid = re.search(r"(\d{4}\.\d{4,5})", e.find("a:id", ns).text).group(1)
        doi = e.find(ax + "doi")
        out[aid] = {"title": re.sub(r"\s+", " ", e.find("a:title", ns).text).strip(),
                    "authors": [n.text for n in e.findall("a:author/a:name", ns)],
                    "date": e.find("a:published", ns).text[:7],
                    "journal_doi": (doi.text.strip().lower() if doi is not None and doi.text else "")}
    return out


def crossref(doi):
    d = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    return json.loads(d)["message"] if d else None


def initials(given):
    return " ".join("-".join(p[0] + "." for p in w.split("-") if p) for w in given.split())


def has_yan(names):
    return any(re.search(r"\bQ(imin|\.)?\s*Yan\b", n) for n in names)


def known_coauthor(names):
    fams = {n.split()[-1].lower() for n in names if n.split()}
    return len(fams & COLLAB) >= 1


def group_first(given, family):
    for g, f in GROUP:
        if family.lower() == f.lower() and given.split()[0].lower().startswith(g.split("-")[0].lower()):
            return FIRST_NAME.get(g, g)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=18)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    since = (dt.date.today() - dt.timedelta(days=30 * a.months)).isoformat()
    bib, have_doi, have_arx, titles, extra = existing()
    news = json.loads((ROOT / "data/news.json").read_text())

    o_doi, o_arx = orcid_ids()
    x_doi, x_arx = openalex_ids(since)
    cand_doi = (o_doi | x_doi) - have_doi
    cand_arx = (o_arx | x_arx) - have_arx
    needs = []
    for aid, (names, pub) in arxiv_search().items():
        if aid in have_arx or aid in cand_arx or pub < since:
            continue
        if has_yan(names) and known_coauthor(names):
            cand_arx.add(aid)
        elif has_yan(names):
            needs.append(f"arXiv:{aid}: '{names[0]} et al.': Q. Yan with no known co-author; check whether it is yours")

    added_bib, added_extra, added_news, replaced = [], [], [], []
    for doi in sorted(cand_doi):
        m = crossref(doi)
        if not m:
            needs.append(f"doi:{doi}: Crossref record not found")
            continue
        if m.get("type") not in ("journal-article", "proceedings-article", "book-chapter"):
            continue
        title = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", (m.get("title") or [""])[0]))).strip()
        date = (m.get("published-online") or m.get("published-print") or m.get("issued") or {}).get("date-parts", [[None]])[0]
        if not title or not date or not date[0] or date[0] < int(since[:4]):
            continue
        bib_titles = [norm(t) for t in re.findall(r"\btitle\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", bib)]
        if seen_title(title, bib_titles):  # already listed (journal entry, or an arXiv entry in the bib)
            continue
        # a preprint in extra_pubs.json now published: drop the preprint entry, add the journal version
        for x in list(extra):
            if difflib.SequenceMatcher(None, norm(x["title"]), norm(title)).ratio() > 0.92:
                extra.remove(x)
                replaced.append(f"{x['venue']} → {doi}")
        auth = m.get("author") or []
        names = [f"{x.get('given', '')} {x.get('family', '')}".strip() for x in auth]
        if not auth or not has_yan(names):
            needs.append(f"doi:{doi}: '{title[:80]}': author list missing or without Q. Yan")
            continue
        journal = (m.get("container-title") or [""])[0]
        vol = m.get("volume", "")
        pages = m.get("page") or m.get("article-number") or ""
        year = str(date[0])
        key = re.sub(r"[^a-z]", "", (auth[0].get("family") or "x").lower()) + year + \
            "".join(w[0] for w in re.findall(r"[A-Za-z]+", journal)[:4]).lower()
        while key in bib:
            key += "b"
        btitle = re.sub(r"(\b[A-Z][a-z]*[A-Z0-9]\w*|\b[A-Z]{2,}\w*)", r"{\1}", title)
        authors = " and ".join(f"{x.get('family', '')}, {x.get('given', '')}".strip(", ") for x in auth)
        entry = (f"@article{{{key},\n  title = {{{btitle}}},\n  author = {{{authors}}},\n  journal = {{{journal}}},\n"
                 + (f"  volume = {{{vol}}},\n" if vol else "") + (f"  pages = {{{pages}}},\n" if pages else "")
                 + f"  year = {{{year}}},\n  doi = {{{doi}}},\n  note = {{verified: crossref}},\n  cv_number = {{new}}\n}}\n")
        bib = bib.rstrip() + "\n\n" + entry
        titles.append(norm(title))
        added_bib.append(f"{', '.join(names[:3])}{' et al.' if len(names) > 3 else ''}, “{title},” {journal} {vol} ({year}). https://doi.org/{doi}")
        first = group_first(auth[0].get("given", ""), auth[0].get("family", ""))
        jhtml = f"<i>{html.escape(journal)}</i>"
        text = (f"The work “{html.escape(title)}” is published in {jhtml}. Congratulations, {first}!" if first
                else f"Our work “{html.escape(title)}” is published in {jhtml}." if (auth[-1].get("family") == "Yan")
                else f"Our collaborative work “{html.escape(title)}” is published in {jhtml}.")
        added_news.append({"date": f"{date[0]}-{date[1]:02d}" if len(date) > 1 and date[1] else year, "text": text,
                           "link": f"https://doi.org/{doi}"})

    metas = arxiv_meta_batch(cand_arx)
    for aid in sorted(cand_arx):
        meta = metas.get(aid)
        if not meta or not has_yan(meta["authors"]):
            needs.append(f"arXiv:{aid}: metadata unavailable or no Q. Yan")
            continue
        if meta["date"] < since[:7]:
            continue  # older preprint (its journal version is normally already listed)
        if meta["journal_doi"] and (meta["journal_doi"] in have_doi or meta["journal_doi"] in cand_doi):
            continue  # published version already listed or being added
        if seen_title(meta["title"], titles):
            continue
        short = []
        for n in meta["authors"]:
            parts = n.split()
            short.append(f"{initials(' '.join(parts[:-1]))} {parts[-1]}".strip())
        extra.append({"key": f"arxiv{aid.replace('.', '')}", "year": meta["date"][:4], "authors": ", ".join(short),
                      "title": meta["title"], "venue": f"arXiv:{aid}", "url": f"https://arxiv.org/abs/{aid}"})
        titles.append(norm(meta["title"]))
        added_extra.append(f"{', '.join(short)}, “{meta['title']},” arXiv:{aid} ({meta['date'][:4]})")
        p = meta["authors"][0].split()
        first = group_first(" ".join(p[:-1]), p[-1])
        added_news.append({"date": meta["date"], "text": f"New preprint: “{html.escape(meta['title'])}”."
                           + (f" Congratulations, {first}!" if first else ""), "link": f"https://arxiv.org/abs/{aid}"})

    changed = bool(added_bib or added_extra or replaced)
    if changed and not a.dry_run:
        (ROOT / "data/publications.bib").write_text(bib if bib.endswith("\n") else bib + "\n")
        (ROOT / "data/extra_pubs.json").write_text(json.dumps(extra, indent=2, ensure_ascii=False) + "\n")
        news = sorted(news + added_news, key=lambda x: x["date"], reverse=True)
        (ROOT / "data/news.json").write_text(json.dumps(news, indent=2, ensure_ascii=False) + "\n")
    month = dt.date.today().strftime("%Y-%m")
    body = [f"Automated publication check ({month}). Sources: ORCID {ORCID}, OpenAlex, arXiv; metadata verified "
            "against Crossref / arXiv. **Please review the news wording before merging**; edit `data/news.json` in this PR.", ""]
    for title, items in (("Added journal papers", added_bib), ("Added preprints", added_extra),
                         ("Preprints replaced by their published version", replaced),
                         ("Draft news items", [f"{n['date']}: {re.sub('<[^>]+>', '', n['text'])}" for n in added_news]),
                         ("Needs confirmation (not added)", needs)):
        if items:
            body += [f"### {title}", ""] + [f"- {i}" for i in items] + [""]
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/pr_body.md").write_text("\n".join(body) + "\n")
    print("\n".join(body))
    print(f"changed={'true' if changed else 'false'}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\nmonth={month}\n")


if __name__ == "__main__":
    main()
