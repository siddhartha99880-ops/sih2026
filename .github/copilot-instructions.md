# Land Intelligence Platform

This repository is a prototype for document digitization, human verification, geospatial validation, infrastructure impact analysis, explainable acquisition risk, and tamper-evident auditing.

## Non-negotiable architecture

- Keep frontend, backend, ML, GIS, and audit modules separated.
- Frontend communicates only with versioned FastAPI REST APIs.
- Keep routes thin; put business logic in services.
- Keep persistence models separate from Pydantic API schemas.
- Keep OCR, computer vision, and risk implementations behind replaceable interfaces.
- Use PostGIS for authoritative persisted spatial operations.
- Use explicit SRIDs and projected CRSs for area calculations.

## Trust and privacy

- AI proposes; deterministic validation checks; a human verifies.
- Never treat geometric intersection as fraud or legal dispute automatically.
- Never claim official ULPIN issuance, legal ownership, government integration, or a trained prediction model without evidence and authority.
- Use synthetic or explicitly authorized data only.
- Never hardcode or log secrets, commit `.env`, or expose server-side secrets through frontend variables.
- Do not store PDFs, images, PII, or complete land records on a blockchain. Hash important state changes instead.

## MVP order

Implement in small runnable phases: health and configuration, documents/parcels, deterministic GIS validation, infrastructure intersections, rules-based risk, human verification, audit hashing, then the verifier UI and CI.