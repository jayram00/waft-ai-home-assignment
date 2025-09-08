#!/usr/bin/env bash
set -euo pipefail

# 1) Compose up
docker compose up -d --build
sleep 5

# 2) Ingest
docker compose run --rm worker python -m app.workers.pipeline --ingest data/input

# 3) Quick smoke tests
curl -s localhost:8000/indicators/domain | jq '.items | length'
curl -s localhost:8000/search -X POST -H 'content-type: application/json' -d '{"query":"disinformation campaign France"}' | jq '.'
