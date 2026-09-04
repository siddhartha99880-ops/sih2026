# API contract

The API is versioned under `/api/v1`. The first vertical-slice endpoint is:

```text
POST /api/v1/analyses
```

It accepts synthetic or authorized parcel data, a polygon and an optional infrastructure corridor. Geometry contracts require EPSG:3857 projected coordinates for this prototype so area is calculated in square metres. Production imports must transform source data into an appropriate local projected CRS and preserve the source CRS in metadata.

Example request:

```json
{
  "parcel_id": "PARCEL-001",
  "fields": {
    "khasra_number": "214",
    "owner_name": "Synthetic Owner",
    "recorded_area_m2": 1200,
    "ownership_count": 2,
    "dispute_indicator": false,
    "acquisition_stage_delay_days": 0
  },
  "parcel": {
    "type": "Polygon",
    "srid": 3857,
    "coordinates": [[[0, 0], [30, 0], [30, 30], [0, 30], [0, 0]]]
  },
  "corridor": {
    "type": "LineString",
    "srid": 3857,
    "coordinates": [[-5, 15], [35, 15]]
  }
}
```

The response includes calculated area, area difference, corridor impact, validation findings, a transparent risk score with factors, lifecycle status, and a SHA-256 record hash. `CONFLICT` means the item needs human review; it is not a legal finding.

The health endpoint is:

```text
GET /api/v1/health
```

## Documents

```text
POST   /api/v1/documents
GET    /api/v1/documents
GET    /api/v1/documents/{document_id}
GET    /api/v1/documents/{document_id}/download
DELETE /api/v1/documents/{document_id}
```

Upload uses multipart form data with `file`, optional `parcel_id`, and optional `document_type`. PDFs, JPEGs, and PNGs up to `MAX_DOCUMENT_SIZE_MB` are accepted after extension, declared MIME, and basic file-signature checks. Files are stored locally under `DOCUMENT_STORAGE_PATH` with generated names; absolute paths are never returned. Uploaded records end at `READY_FOR_OCR`. No OCR is performed in this phase.