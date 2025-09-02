import pathlib
import textwrap
import json

ROOT = pathlib.Path(".").resolve()

DIRS = [
  "scripts/cli", "scripts/vectorizers", "scripts/experiments/ridge/config",
  "scripts/experiments/logistic", "scripts/experiments/federated",
  "scripts/tables", "scripts/dpia", "scripts/ci",
  "data/raw", "data/external", "data/interim", "data/processed",
  "results/figures", "results/tables", "results/logs", "results/artifacts",
  "results/uploads/catalogs", "results/uploads/ga_csv",
  "notebooks/exploration", "notebooks/profiling",
  "backend/src/aggregator/routes", "backend/src/he_core/backends", "backend/src/he_core/multiparty",
  "backend/src/infra", "backend/src/worker", "backend/tests/unit",
  "backend/tests/integration", "backend/tests/property", "backend/tests/fuzz",
  "backend/tests/e2e", "backend/migrations/versions", "backend/scripts", "backend/docker",
  "backend/.github/workflows", "web/src/components", "web/src/lib", "web/src/pages",
  "web/src/generated", "web/tests/fixtures", "infra/devcontainer", "infra/k8s", "infra/docker/traefik",
  "infra/terraform", "benchmarks", ".github/workflows", ".github/ISSUE_TEMPLATE", "docs/pages", "docs/diagrams",
  "docs/_static", "docs/_templates", ".dvc"
]

FILES = {
  "LICENSE": "MIT\n",
  "CITATION.cff": "title: HE Retail Analytics\nmessage: If you use this project, please cite it.\n",
  "SECURITY.md": "# Security Policy\n\nReport vulnerabilities via GitHub Security Advisories.\n",
  "CODE_OF_CONDUCT.md": "# Code of Conduct\n\nBe excellent to each other.\n",
  "CONTRIBUTING.md": "# Contributing\n\n1. Fork\n2. Feature branch\n3. PR with tests\n",
  "CHANGELOG.md": "# Changelog\n\n",
  ".editorconfig": "[*]\nend_of_line = lf\ninsert_final_newline = true\ncharset = utf-8\nindent_style = space\nindent_size = 2\n",
  ".env.example": "API_KEY=devkey\nDB_URL=sqlite:///results/he.sqlite\nREDIS_URL=redis://localhost:6379/0\n",
  "Makefile": "init:\n\tpython -m pip install --upgrade pip\n\tpre-commit install\n",
  "justfile": "init: \n\t@echo 'use make or scripts'\n",
  ".pre-commit-config.yaml": "repos:\n- repo: https://github.com/astral-sh/ruff-pre-commit\n  rev: v0.5.7\n  hooks:\n    - id: ruff\n    - id: ruff-format\n- repo: https://github.com/pre-commit/mirrors-mypy\n  rev: v1.10.0\n  hooks:\n    - id: mypy\n",
  ".github/PULL_REQUEST_TEMPLATE.md": "## Summary\n\n## Tests\n\n## Notes\n",
  ".github/ISSUE_TEMPLATE/bug_report.md": "---\nname: Bug report\nabout: Create a report to help us improve\n---\n",
  ".github/ISSUE_TEMPLATE/feature_request.md": "---\nname: Feature request\nabout: Suggest an idea\n---\n",
  ".github/dependabot.yml": "version: 2\nupdates:\n  - package-ecosystem: pip\n    directory: \"/backend\"\n    schedule:\n      interval: weekly\n  - package-ecosystem: npm\n    directory: \"/web\"\n    schedule:\n      interval: weekly\n",
  ".github/workflows/web-ci.yml": "name: web-ci\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v4\n    - uses: actions/setup-node@v4\n      with: { node-version: 'lts/*' }\n    - run: corepack enable && pnpm i\n      working-directory: web\n    - run: pnpm -C web build\n",
  ".github/workflows/release-drafter.yml": "name: Release Drafter\non:\n  push:\n    branches: [ main ]\n  pull_request:\n    types: [opened, edited, reopened, closed]\njobs:\n  update:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: release-drafter/release-drafter@v6\n      env:\n        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n",
  ".github/workflows/sbom-scan.yml": "name: sbom-scan\non: [push]\njobs:\n  sbom:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v4\n    - uses: anchore/sbom-action@v0\n      with:\n        path: .\n        format: spdx-json\n",
  "scripts/ci/codegen_ts_client.sh": "#!/usr/bin/env bash\nset -euo pipefail\nAPI=${1:-http://localhost:8000/openapi.json}\nOUT=${2:-../../web/src/generated/types.ts}\nnpx --yes openapi-typescript \"$API\" -o \"$OUT\"\necho \"Generated $OUT\"\n",
  "scripts/cli/hepp.py": "import json, time\nprint(json.dumps({'progress':0.5,'msg':'half'})); print('hello')\n",
  "scripts/tables/export_appendix_xlsx.py": "print('stub: export xlsx')\n",
  "scripts/tables/latex_tablegen.py": "print('stub: latex tables')\n",
  "scripts/vectorizers/uci_online_retail.py": "print('stub: uci loader')\n",
  "scripts/vectorizers/ga_sample.py": "print('stub: ga loader')\n",
  "scripts/experiments/ridge/run.py": "print('stub: ridge run')\n",
  "scripts/experiments/ridge/config/default.yaml": "d: 256\n",
  "scripts/experiments/ridge/config/ablations.yaml": "batch_sizes: [1,8,32]\n",
  "scripts/experiments/logistic/run.py": "print('stub: logistic run')\n",
  "scripts/experiments/federated/run.py": "print('stub: federated run')\n",
  "scripts/dpia/dpia_generator.py": "print('stub: dpia')\n",
  "backend/README.md": "# Backend\n",
  "backend/.env.example": "API_KEY=devkey\nCORS_ALLOW_ORIGINS=http://localhost:5173\nDB_URL=sqlite:///results/he.sqlite\nREDIS_URL=redis://localhost:6379/0\n",
  "backend/Makefile": "run:\n\tuvicorn src.aggregator.api:app --host 0.0.0.0 --port 8000 --reload\n",
  "backend/justfile": "run:\n\tuvicorn src.aggregator.api:app --host 0.0.0.0 --port 8000 --reload\n",
  "backend/pyproject.toml": "[build-system]\nrequires=['setuptools','wheel']\nbuild-backend='setuptools.build_meta'\n[project]\nname='he-backend'\nversion='0.0.1'\nrequires-python='>=3.12'\ndependencies=['fastapi','uvicorn[standard]','sqlmodel','alembic','redis','rq','pydantic','python-multipart','prometheus-client','typer']\n",
  "backend/src/aggregator/api.py": "from fastapi import FastAPI\napp=FastAPI(title='HE API')\n@app.get('/healthz')\ndef health(): return {'ok': True}\n",
  "backend/src/aggregator/jobs_runtime.py": "STORE=None  # fill later\n",
  "backend/src/aggregator/routes/jobs.py": "from fastapi import APIRouter\nrouter=APIRouter(prefix='/api/v1/jobs')\n",
  "backend/src/aggregator/routes/upload.py": "from fastapi import APIRouter\nrouter=APIRouter(prefix='/api/v1/upload')\n",
  "backend/src/he_core/__init__.py": "",
  "backend/src/he_core/utils.py": "",
  "backend/src/he_core/ops_ml.py": "",
  "backend/src/he_core/aggregation.py": "",
  "backend/src/he_core/backends/__init__.py": "",
  "backend/src/he_core/backends/tenseal_backend.py": "",
  "backend/src/he_core/backends/openfhe_backend.py": "",
  "backend/src/he_core/multiparty/__init__.py": "",
  "backend/src/he_core/multiparty/threshold_api.py": "",
  "backend/src/he_core/multiparty/threshold_openfhe.py": "",
  "backend/src/infra/__init__.py": "",
  "backend/src/infra/db.py": "",
  "backend/src/infra/queue.py": "",
  "backend/src/infra/security.py": "",
  "backend/src/infra/settings.py": "",
  "backend/src/worker/__init__.py": "",
  "backend/src/worker/worker.py": "",
  "backend/src/worker/tasks.py": "",
  "backend/migrations/env.py": "from alembic import context\n",
  "backend/scripts/codegen_ts_client.sh": "#!/usr/bin/env bash\necho codegen stub\n",
  "backend/docker/Dockerfile.api": "FROM python:3.12-slim\n",
  "backend/docker/Dockerfile.worker": "FROM python:3.12-slim\n",
  "backend/docker/compose.dev.yml": "services: {}\n",
  "backend/.github/workflows/backend-ci.yml": "name: backend-ci\non:[push]\njobs:{test:{runs-on:ubuntu-latest,steps:[{uses:'actions/checkout@v4'}]}}\n",
  "backend/tests/unit/test_api_health.py": "from fastapi.testclient import TestClient\nfrom src.aggregator.api import app\n\ndef test_health():\n    c=TestClient(app)\n    r=c.get('/healthz')\n    assert r.status_code==200 and r.json()['ok'] is True\n",
  "web/README.md": "# Web\n",
  "web/package.json": json.dumps({"name":"he-web","private":True,"version":"0.0.1","type":"module","scripts":{"dev":"vite","build":"vite build","preview":"vite preview","test":"vitest"}}, indent=2),
  "web/tsconfig.json": json.dumps({"compilerOptions":{"target":"ES2020","module":"ESNext","jsx":"react-jsx","moduleResolution":"bundler","strict":True,"skipLibCheck":True,"baseUrl":"./","paths":{"@/*":["src/*"]}},"include":["src"]}, indent=2),
  "web/vite.config.ts": "import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react'; export default defineConfig({plugins:[react()],server:{port:5173}})\n",
  "web/vitest.config.ts": "import { defineConfig } from 'vitest/config'; export default defineConfig({ test:{ environment:'jsdom' } })\n",
  "web/tailwind.config.js": "export default { content: ['./index.html','./src/**/*.{ts,tsx}'], theme:{extend:{}}, plugins:[] }\n",
  "web/postcss.config.js": "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }\n",
  "web/.env.local.example": "VITE_API_BASE=http://localhost:8000\nVITE_AUTH_MODE=apiKey\n",
  "web/src/main.tsx": "console.log('stub ui')\n",
  "web/src/App.tsx": "export default function App(){ return null }\n",
  "web/src/index.css": "@tailwind base; @tailwind components; @tailwind utilities;\n",
  "web/src/routes.tsx": "export default [] as const\n",
  "web/src/components/NavBar.tsx": "",
  "web/src/components/Protected.tsx": "",
  "web/src/lib/env.ts": "export const ENV={API_BASE: import.meta.env.VITE_API_BASE||''}\n",
  "web/src/lib/api.ts": "export {}\n",
  "web/src/lib/auth.ts": "export {}\n",
  "web/src/lib/authmode.ts": "export {}\n",
  "web/src/lib/sse.ts": "export {}\n",
  "web/src/pages/Login.tsx": "",
  "web/src/pages/OidcCallback.tsx": "",
  "web/src/pages/Dashboard.tsx": "",
  "web/src/pages/Jobs.tsx": "",
  "web/src/pages/JobsDetail.tsx": "",
  "web/src/generated/types.ts": "// generated types will land here\n",
  "web/tests/fixtures/sample_catalog.csv": "category,amount\nA,10\nB,20\n",
  "infra/devcontainer/.devcontainer.json": "{\n  \"name\": \"he-retail-analytics\",\n  \"build\": { \"dockerfile\": \"Dockerfile\" },\n  \"features\": {},\n  \"postCreateCommand\": \"pip install -e backend[dev,tests] && corepack enable && pnpm -C web i\"\n}\n",
  "infra/devcontainer/Dockerfile": "FROM mcr.microsoft.com/devcontainers/python:3.12\nRUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*\n",
  "infra/k8s/api-deployment.yaml": "# k8s stub\n",
  "infra/k8s/worker-deployment.yaml": "# k8s stub\n",
  "infra/k8s/redis-deployment.yaml": "# k8s stub\n",
  "infra/k8s/postgres-statefulset.yaml": "# k8s stub\n",
  "infra/docker/compose.local.yml": "services: {}\n",
  "infra/docker/traefik/traefik.yml": "log: { level: INFO }\n",
  "infra/terraform/README.md": "# Terraform stub\n",
  "benchmarks/asv.conf.json": "{ \"version\": 1, \"project\":\"he-retail-analytics\", \"env_name\":\"conda-py3.12\" }\n",
  "benchmarks/bench_ops.py": "def time_stub():\n    pass\n",
  "docs/pages/reproducing-figures.md": "# Reproducing all figures\n\n`hepp make-all` or `hepp make-all-ga`\n",
  "docs/pages/parameter-selection.md": "# CKKS parameter selection\n",
  "docs/pages/data-profiling.md": "# Data profiling\n",
  "docs/pages/curated-catalog-demo.md": "# Curated vs hashed\n",
  "docs/pages/security-dpia.md": "# DPIA\n",
  "docs/pages/api/reference.md": "# API Reference (auto)\n",
  "docs/diagrams/system_overview.gv": "digraph G { UI->API; API->Worker; Worker->Redis; }\n",
  "docs/diagrams/crypto_flow.gv": "digraph G { keygen->encrypt->aggregate->threshold_decrypt }\n",
  ".dvc/.gitkeep": ""
}

def ensure_dirs():
    for d in DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
        # drop .gitkeep for empty dirs
        if not any((ROOT/d).iterdir()):
            (ROOT / d / ".gitkeep").write_text("", encoding="utf-8")

def write_files():
    for path, content in FILES.items():
        p = ROOT / path
        if p.exists():
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, dict):
            p.write_text(json.dumps(content, indent=2), encoding="utf-8")
        else:
            p.write_text(textwrap.dedent(content), encoding="utf-8")

if __name__ == "__main__":
    ensure_dirs()
    write_files()
    print("Scaffold completed without overwriting existing files.")
	