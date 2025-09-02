import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from src.aggregator.api import create_app  # build the app after setting env

@pytest.mark.asyncio
async def test_job_flow(tmp_path, monkeypatch):
    # Isolate results/DB per test
    results = tmp_path / "results"
    results.mkdir()
    monkeypatch.setenv("RESULTS_DIR", str(results))
    monkeypatch.setenv("DB_URL", f"sqlite:///{results}/he.sqlite")
    monkeypatch.setenv("API_KEY", "devkey")

    app = create_app()  # env must be set before this
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # health
        r = await ac.get("/healthz")
        assert r.status_code == 200

        # create a job with header auth
        r = await ac.post(
            "/api/v1/jobs/make-all-ga",
            headers={"X-API-Key": "devkey"},
            json={"ga_csv": "demo.csv", "d": 256},
        )
        assert r.status_code == 200
        job_id = r.json()["id"]

        # poll until done
        for _ in range(60):
            r = await ac.get(f"/api/v1/jobs/{job_id}", headers={"X-API-Key": "devkey"})
            assert r.status_code == 200
            if r.json()["status"] in ("succeeded", "failed"):
                break
            await asyncio.sleep(0.1)
        assert r.json()["status"] == "succeeded"

        # artifacts should include hello.txt
        r = await ac.get(f"/api/v1/jobs/{job_id}/artifacts", headers={"X-API-Key": "devkey"})
        assert r.status_code == 200
        arts = r.json()
        assert any(a["name"] == "hello.txt" for a in arts)

        # served file
        r = await ac.get("/files/figures/hello.txt")
        assert r.status_code == 200
        assert r.text.strip() == "demo artifact"

@pytest.mark.asyncio
async def test_healthz(tmp_path, monkeypatch):
    # isolate env
    results = tmp_path / "results"
    results.mkdir()
    monkeypatch.setenv("RESULTS_DIR", str(results))
    monkeypatch.setenv("DB_URL", f"sqlite:///{results}/he.sqlite")

    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"ok": True}
