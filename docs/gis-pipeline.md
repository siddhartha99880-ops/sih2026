# GIS pipeline

The initial analysis contract accepts projected EPSG:3857 coordinates and calculates synthetic demo areas in square metres with Shapely. Production ingestion must validate the source CRS and transform into an appropriate local projected CRS before authoritative PostGIS operations.

Validation outcomes are deliberately narrow:

- geometry validity
- recorded versus calculated area difference
- spatial corridor impact

A corridor intersection is reported as `SPATIAL_CONFLICT` and requires human review. It is not automatically fraud, a dispute, or a legal conclusion.

Area thresholds are configurable: up to 5% is a pass, above 5% through 10% is a warning, and above 10% is a conflict.
