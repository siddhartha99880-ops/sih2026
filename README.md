# Land Intelligence Platform

A prototype workflow for turning legacy land records into spatially validated infrastructure-acquisition intelligence.

The first vertical slice is:

```text
synthetic deed/map -> extraction -> human review -> GIS validation -> corridor impact -> explainable risk -> audit hash
```

AI output is advisory. A human must verify a record. The prototype does not issue official ULPIN identifiers, determine legal ownership, or represent official government data.

## Repository layout

- `backend/`: FastAPI API and domain services
- `frontend/`: verifier-first web client (next implementation phase)
- `ml-engine/`: replaceable OCR, boundary, and risk adapters
- `blockchain/`: optional ledger adapter; local hash chain comes first
- `docs/`: architecture and operating decisions
- `data/sample/`: synthetic demo fixtures only

## Local start

Requirements: Python 3.11+, Docker, and Docker Compose.

```bash
cp .env.example .env
make install-backend
make test
make run-backend
```

The API is available at `http://localhost:8000` and its OpenAPI document at `http://localhost:8000/docs`.

Start the database with `docker compose up -d postgres`. The health endpoint remains useful without the database during the initial scaffold, but persistence features require PostGIS.

## Development phases

1. Foundation and API contracts
2. Documents and parcels
3. Deterministic GIS validation
4. Infrastructure intersection
5. Explainable risk
6. Human verification and audit
7. Verifier UI and CI hardening

Use synthetic or explicitly authorized data. Never commit `.env`, private records, credentials, or model weights.
