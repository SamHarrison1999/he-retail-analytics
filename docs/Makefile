# docs/Makefile

# Prefer active venv; else repo .venv; else python; else python3
PY ?= $(shell \
  if [ -n "$$VIRTUAL_ENV" ] && [ -x "$$VIRTUAL_ENV/bin/python" ]; then echo "$$VIRTUAL_ENV/bin/python"; \
  elif [ -x "$(CURDIR)/../.venv/bin/python" ]; then echo "$(CURDIR)/../.venv/bin/python"; \
  elif command -v python >/dev/null 2>&1; then command -v python; \
  else command -v python3; fi)

SOURCEDIR = source
BUILDDIR  = build
PORT ?= 8000

.PHONY: html serve open stop clean watch

html:
	$(PY) -m sphinx -b html $(SOURCEDIR) $(BUILDDIR)/html

serve:
	$(PY) -m http.server --directory $(BUILDDIR)/html $(PORT)

open:
	@powershell.exe -NoProfile -Command Start-Process http://localhost:$(PORT)/index.html

stop:
	@fuser -k $(PORT)/tcp 2>/dev/null || pkill -f "http.server.*$(PORT)" || true

clean:
	rm -rf $(BUILDDIR)

watch:
	$(PY) -m sphinx_autobuild $(SOURCEDIR) $(BUILDDIR)/html --port $(PORT)
