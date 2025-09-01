.PHONY: run test lint type clean
VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

init:
	python3.12 -m venv $(VENV)
	$(PIP) install -e ".[dev]"

run:
	RESULTS_DIR=$$(realpath ../results) \
	DB_URL=sqlite:///$$(realpath ../results)/he.sqlite \
	API_KEY=devkey \
	CORS_ALLOW_ORIGINS=http://localhost:5173 \
	$(VENV)/bin/uvicorn src.aggregator.api:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest --cov=src --cov-report=term-missing

lint:
	ruff check .

type:
	mypy src

clean:
	rm -rf $(VENV) .pytest_cache __pycache__
