from fastapi.testclient import TestClient
from src.aggregator.api import app

def test_health():
    c=TestClient(app)
    r=c.get('/healthz')
    assert r.status_code==200 and r.json()['ok'] is True
