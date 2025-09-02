<!--
Use a conventional commit style title, e.g.:
feat(api): add jobs SSE stream and artifact listing
fix(web): handle SSE disconnects on job detail
docs: add parameter-selection page

Please keep the body sections below — reviewers rely on them.
-->

## Summary
<!-- What does this PR do in one or two sentences? Why now? -->

## Motivation / Context
<!-- Problem statement, goals, non-goals. Link prior phases/plan where relevant. -->

## Type of change
- [ ] feat (new feature)
- [ ] fix (bug fix)
- [ ] docs (documentation only)
- [ ] refactor (no behavior change)
- [ ] perf (performance improvement)
- [ ] ci (build/CI/CD)
- [ ] chore (maintenance / tooling)

## Changes
<!-- Bullet the key changes. If large, group by area (backend/web/scripts/docs/infra). -->
- Backend:
- Web:
- Scripts/CLI:
- Docs:
- Infra/CI:

## How to run / verify locally
<!-- Exact commands. Keep copy/paste friendly. -->
```bash
# Backend
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,tests]" || pip install fastapi uvicorn[standard] sqlmodel alembic prometheus-client python-multipart typer
export API_KEY=devkey CORS_ALLOW_ORIGINS=http://localhost:5173
uvicorn src.aggregator.api:app --reload

# Web
cd web
corepack enable && pnpm i
cp .env.local.example .env.local
pnpm dev
```
- Navigate to: http://localhost:5173
- Test flow: …

## Screenshots / Logs
<!-- If UI or logs change, include before/after images or representative log lines. -->

## API / DB / Config changes
- API surface changed?  - [ ] No  - [ ] Yes (details below)
- DB schema/migration?  - [ ] No  - [ ] Yes (`alembic` revision: …)
- New env vars?         - [ ] No  - [ ] Yes (documented in `.env.example`)
- Files served from `/files`? - [ ] No  - [ ] Yes (paths: …)

**Details (if any):**
<!-- Endpoints added/modified, payloads, error codes, versioning strategy, migrations/backfills. -->

## Security & Privacy
- [ ] Input validation added/updated (size/type caps)
- [ ] AuthZ/AuthN unchanged or improved
- [ ] CORS/rate limiting sane for new endpoints
- [ ] No secrets committed; `.env.example` updated
- [ ] Data handling respects “no PII, aggregates only” principle

Notes:
<!-- Threat model notes, misuse risks, DPIA impact if any. -->

## Performance & Observability
- [ ] Adds/updates Prometheus metrics
- [ ] Benchmark or latency impact considered
- [ ] Dashboards updated (if relevant)

Notes:
<!-- Expected QPS/latency/CPU, metrics names, panels affected. -->

## Testing
- Unit tests:  [ ] added / [ ] updated / [ ] n/a
- Integration: [ ] added / [ ] updated / [ ] n/a
- E2E/UI:      [ ] added / [ ] updated / [ ] n/a
- Property/Fuzz (if parser/IO touched): [ ] added / [ ] n/a
- Coverage: baseline → new = **__% → __%**
- Mutation tests (if applicable): [ ] ran / [ ] n/a

How to run:
```bash
# Backend tests
cd backend && pytest -q --cov=src --cov-report=term-missing

# Web tests
cd web && pnpm test
# E2E (if configured)
pnpm exec playwright test
```

## Docs Updated?
- [ ] Not needed
- [ ] Yes — links:
  - pages: …
  - diagrams: …
  - API reference: …
  - “Reproducing all figures” commands updated

## Release Notes
<!-- One or two lines for CHANGELOG/release drafter. -->

## Breaking Changes / Migration
- [ ] None
- [ ] Yes — describe migration/backout steps:

## Rollout / Backout Plan
- Rollout: …
- Backout: …
- Data/DB cleanup (if any): …

## Definition of Done
- [ ] Builds & tests green locally
- [ ] Pre-commit passes (ruff, mypy, etc.)
- [ ] CI green (scoped workflows where appropriate)
- [ ] Coverage meets gate (≥85% or project default)
- [ ] SBOM/vuln scan pass (if building images)
- [ ] `.env.example` reflects any new vars
- [ ] Documentation updated (if user-facing)

## Checklist
- [ ] No large binary files added unintentionally
- [ ] No TODOs left in diff (or tracked via issues)
- [ ] Issue references included
- [ ] Conventional commit title

## Linked Issues / Epics
- Closes #
- Relates to #

## Notes for Reviewers
<!-- Call out tricky parts, suggested review order, and any follow-up PRs you plan. -->