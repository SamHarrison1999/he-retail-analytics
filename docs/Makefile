# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)



PY    ?= python3
PORT  ?= 8000
SOURCEDIR = source
BUILDDIR  = build

.PHONY: html serve open stop watch

html:
	$(PY) -m sphinx -b html $(SOURCEDIR) $(BUILDDIR)/html

serve:
	@$(PY) -m http.server --directory $(BUILDDIR)/html $(PORT)

open:
	@powershell.exe -NoProfile -Command Start-Process http://localhost:$(PORT)/index.html

stop:
	@fuser -k $(PORT)/tcp 2>/dev/null || pkill -f "http.server.*$(PORT)" || true

watch:
	@sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html --port $(PORT)
