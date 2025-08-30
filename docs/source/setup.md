# Setup

Below reproduces the toolchain used on Ubuntu 24.04 (Noble), WSL-friendly.

## System deps

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake ninja-build pkg-config \
  python3 python3-venv python3-dev \
  libomp-dev libopenblas-dev libgmp-dev libssl-dev \
  graphviz git curl unzip
```

Optional for `pygraphviz`:

```bash
sudo apt install -y graphviz-dev
```

## Python (3.12) env

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install numpy scipy matplotlib jupyter rich graphviz
```

## Node LTS and pnpm

```bash
# nvm
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
nvm install --lts
corepack enable
corepack prepare pnpm@latest --activate
```

## Sphinx docs

```bash
python -m pip install -U sphinx myst-parser sphinx-copybutton sphinx-autobuild sphinxcontrib-mermaid
# enable extensions in docs/source/conf.py:
#
# extensions = [
#   "myst_parser",
#   "sphinx.ext.graphviz",
#   "sphinx_copybutton",
#   "sphinxcontrib.mermaid",
# ]
# graphviz_output_format = "svg"
```
