# Architecture

The prototype follows this flow:

```text
document/map -> extraction adapter -> human review -> deterministic GIS checks
             -> infrastructure intersection -> explainable risk -> audit hash
```

FastAPI routes validate requests and delegate to services. Persistence, OCR, advanced computer vision, and blockchain providers will be introduced behind interfaces without changing the API contract. AI output is advisory and cannot transition a parcel to legally verified status by itself.

The first runnable service keeps analysis in memory and uses Shapely with explicit projected EPSG:3857 coordinates. PostGIS becomes authoritative when parcel persistence and migrations are added.