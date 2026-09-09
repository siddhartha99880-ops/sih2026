export type DocumentStatus = 'UPLOADED' | 'VALIDATED' | 'PROCESSING' | 'READY_FOR_OCR' | 'OCR_COMPLETE' | 'NEEDS_REVIEW' | 'FAILED'
export type DocumentType = 'LAND_DEED' | 'SALE_DEED' | 'KHATA' | 'KHASRA' | 'LAND_RECORD' | 'SURVEY_MAP' | 'OTHER' | 'UNKNOWN'
export type ParcelStatus = 'UPLOADED' | 'PROCESSING' | 'EXTRACTED' | 'NEEDS_REVIEW' | 'VERIFIED' | 'CONFLICT' | 'RESOLVED'
export type Severity = 'PASS' | 'WARNING' | 'CONFLICT' | 'NEEDS_REVIEW'

export interface DocumentRecord {
  id: string
  parcel_id: string | null
  original_filename: string
  mime_type: string
  file_size_bytes: number
  document_type: DocumentType
  status: DocumentStatus
  checksum_sha256: string
  created_at: string
  updated_at: string
}

export interface ParcelRecord {
  id: string
  khasra_number: string
  khata_number: string | null
  state: string
  district: string
  tehsil: string | null
  village: string
  recorded_area_m2: number
  geometry: { type: 'Polygon'; coordinates: number[][][] }
  srid: number
  status: ParcelStatus
  verification_status: string
  confidence_score: number | null
  created_at: string
  updated_at: string
}

export interface ParcelListResponse { items: ParcelRecord[]; total: number; offset: number; limit: number }

export interface ValidationFinding {
  code: string
  severity: Severity
  message: string
  calculated_area_m2?: number | null
  intersection_area_m2?: number | null
  intersection_percentage?: number | null
}

export interface OverlapResult { parcel_id: string; overlap_area_m2: number; overlap_percentage: number }

export interface ValidationResponse {
  parcel_id: string
  geometry_valid: boolean
  calculated_area_m2: number | null
  recorded_area_m2: number | null
  area_difference_m2: number | null
  area_difference_percent: number | null
  overlap_detected: boolean
  overlapping_parcel_ids: string[]
  overlap_results: OverlapResult[]
  result: Severity
  summary: string
  findings: ValidationFinding[]
  overall_severity: Severity
}

export interface InfrastructureProject {
  id: string
  name: string
  project_type: string
  status: string
  corridor_geometry: { type: 'LineString'; coordinates: number[][] }
  srid: number
  created_at: string
  updated_at: string
}

export interface HealthResponse { status: string; environment: string; database: string }