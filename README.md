# qyanlab.net: Yan Group website

Static site for the Yan Group (Department of Physics, Northeastern University), served by GitHub Pages from `docs/`.

- Edit content in `content/*.md` (research, bio, teaching, join, resources) and `data/*.json` (people, news, code,
  extra preprints). Publications come from `data/publications.bib` (verified bibliography).
- Build: `python3 tools/build.py` (requires `pandoc`); preview: `python3 tools/build.py --serve` → http://localhost:8000
- Commit both the sources and `docs/`; GitHub Pages publishes `docs/` at https://www.qyanlab.net
