[![Docs — live](badge.svg)](https://samharrison1999.github.io/he-retail-analytics/)


# HE Retail Analytics

Homomorphic encryption for retail analytics — code, experiments, and thesis docs.

## Getting started
```bash
# clone
git clone git@github.com:SamHarrison1999/he-retail-analytics.git
cd he-retail-analytics

# python env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

# docs deps
pip install -r docs/requirements.txt

# build & serve docs
python -m sphinx -b html docs/source docs/build/html
python -m http.server --directory docs/build/html 8000
# open http://localhost:8000
