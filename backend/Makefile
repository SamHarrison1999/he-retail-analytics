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

.PHONY: api worker redis
ENV = RESULTS_DIR=$(PWD)/results DB_URL=sqlite:///$(PWD)/results/he.sqlite REDIS_URL=redis://localhost:6379/0 API_KEY=devkey

api:
	. .venv/bin/activate && $(ENV) uvicorn src.aggregator.api:app --reload

worker:
	. .venv/bin/activate && $(ENV) python -m src.aggregator.rq_worker

redis:
	docker ps | grep -q redis || docker run -d --name redis -p 6379:6379 redis:7-alpine
