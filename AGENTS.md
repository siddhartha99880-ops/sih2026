# Implementation order

Implement incrementally. Keep each phase runnable before starting the next.

1. Foundation and health endpoint
2. Documents, parcels, and GeoJSON
3. Deterministic PostGIS/Shapely validation
4. Infrastructure intersections
5. Explainable rules-based risk
6. Human verification and SHA-256 audit
7. Verifier UI, fixtures, tests, and CI

Architecture rules:

- Frontend communicates only with FastAPI.
- Routes validate and delegate; business logic belongs in services.
- ML implementations are replaceable adapters and never live in routes.
- AI proposes; deterministic checks validate; a human verifies.
- Use explicit SRIDs and projected CRSs for area calculations.
- Never claim official ULPIN, legal ownership, government data, or a trained risk model without the required authority or evidence.
- Never commit secrets, private records, or real personal data.
