#!/bin/sh
# Production startup for Render: ingest the Jan-2026 data into the parquet cache,
# then launch the API. `|| true` lets the service still start (degraded) if Elexon
# is briefly unreachable; the next successful boot will populate the cache.
set -e

python scripts/ingest.py || echo "ingest failed; starting with existing/empty cache"

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
