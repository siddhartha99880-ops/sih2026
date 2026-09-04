# Demo scenario

1. Start the API with `make run-backend`.
2. Open `/docs` and call `POST /api/v1/analyses` with `data/sample/analysis-request.json`.
3. Observe the 900 m2 calculated parcel against the 1,200 m2 recorded area.
4. Observe the infrastructure corridor intersection and `SPATIAL_CONFLICT` finding.
5. Review the explainable risk factors and `HIGH` risk level.
6. Confirm the response contains a 64-character SHA-256 audit hash.

This is synthetic data. The analysis endpoint currently models the deterministic core while document upload, OCR adapters, PostGIS persistence, human state transitions, and the frontend are subsequent phases.
