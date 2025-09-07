# HE Retail Analytics

Homomorphic encryption for retail analytics — code, experiments, and Sphinx documentation that accompanies the thesis work.

[![Docs (live)](badge.svg)](https://samharrison1999.github.io/he-retail-analytics/)
[![Build & Deploy Sphinx Docs](https://github.com/SamHarrison1999/he-retail-analytics/actions/workflows/pages.yml/badge.svg)](https://github.com/SamHarrison1999/he-retail-analytics/actions/workflows/docs.yml)
[![License: Apache-2.0](https://img.shields.io/badge/Code%20License-Apache--2.0-blue.svg)](LICENSE)
[![Docs License: CC BY 4.0](https://img.shields.io/badge/Docs%20License-CC%20BY%204.0-lightgrey.svg)](docs/LICENSE)

---

## Links

- **Live docs:** https://samharrison1999.github.io/he-retail-analytics/
- **Sitemap:** https://samharrison1999.github.io/he-retail-analytics/sitemap.xml
- **Source repo:** https://github.com/SamHarrison1999/he-retail-analytics

## Repository layout

```text
docs/
  Makefile
  requirements.txt
  source/
    _static/            # favicon, logo, custom assets
    _extra/robots.txt   # served as-is (sitemap hint)
    conf.py             # Sphinx config (Furo, sitemap, OGP, design)
    index.rst           # table of contents
    *.md                # pages (MyST Markdown)
.github/
  workflows/docs.yml    # Build & Deploy Sphinx Docs (GitHub Pages)
badge.svg               # “Docs — live” badge used above
```

## Local docs — quick start (WSL/Ubuntu)

> **Prereqs:** Python 3.12 and Graphviz (`dot`) installed on your system.

1) **Clone and enter**
```bash
git clone git@github.com:SamHarrison1999/he-retail-analytics.git
cd he-retail-analytics
```

2) **Create a venv**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) **Install doc dependencies**
```bash
pip install -U pip
pip install -r docs/requirements.txt
```

4) **Build**
```bash
make -C docs html
```

5) **Serve locally** (default `8000`; change with `PORT=8010` etc.)
```bash
PORT=8010 make -C docs serve &
# then open http://localhost:8010/
```

### WSL tip (open in Windows browser)

If `wslview` is grumpy, just open the local server URL directly:

```bash
powershell.exe -NoProfile -Command "Start-Process 'http://localhost:8010/index.html'"
```

### Troubleshooting

- **Port already in use**
  ```bash
  fuser -k 8010/tcp 2>/dev/null || pkill -f "http.server.*8010"
  ```

- **Use the venv’s Python explicitly**
  ```bash
  ./.venv/bin/python -m sphinx -b html docs/source docs/build/html
  ```

## Continuous deployment (GitHub Pages)

Every push to `main`:

1. Sets up Python and Graphviz.
2. Installs `docs/requirements.txt`.
3. Runs linkcheck in **strict** mode.
4. Builds Sphinx HTML and writes `.nojekyll`.
5. Uploads the artifact and deploys to **GitHub Pages**.

Workflow: `.github/workflows/docs.yml`.

## Licensing

- **Code** (everything outside `docs/`): licensed under the [Apache License 2.0](./LICENSE).  
  _SPDX_: `SPDX-License-Identifier: Apache-2.0`

- **Documentation** (everything in `docs/`): licensed under [Creative Commons Attribution 4.0 International](./docs/LICENSE).  
  _SPDX_: `SPDX-License-Identifier: CC-BY-4.0`

By contributing, you agree your contributions are provided under the same respective terms.  
Note: third-party assets (e.g., logos) may be subject to their own licenses as noted in the docs.


## Contributing

PRs/issues welcome. Please keep doc pages in `docs/source/` and preview locally before submitting.
