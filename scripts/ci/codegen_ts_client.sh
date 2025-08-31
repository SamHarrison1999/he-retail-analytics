#!/usr/bin/env bash
set -euo pipefail
API=${1:-http://localhost:8000/openapi.json}
OUT=${2:-../../web/src/generated/types.ts}
npx --yes openapi-typescript "$API" -o "$OUT"
echo "Generated $OUT"
