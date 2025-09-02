# Backend

## Dev quickstart

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
mkdir -p ../results
export RESULTS_DIR=$(realpath ../results)
export DB_URL=sqlite:///$RESULTS_DIR/he.sqlite
export API_KEY=devkey
export CORS_ALLOW_ORIGINS=http://localhost:5173
uvicorn src.aggregator.api:app --host 0.0.0.0 --port 8000 --reload
```

## Sanity checks
```bash
# new terminal
curl -s http://localhost:8000/healthz
curl -s -H 'X-API-Key: devkey' -H 'content-type: application/json' \
  -d '{"ga_csv":"demo.csv","d":256}' http://localhost:8000/api/v1/jobs/make-all-ga | jq .
# stream logs in another terminal if you like, then:
curl -s http://localhost:8000/files/figures/hello.txt
```