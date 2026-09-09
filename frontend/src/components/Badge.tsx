import type { Severity } from '../types/api'

const labels: Record<string, string> = {
  PASS: 'Passed',
  WARNING: 'Warning',
  CONFLICT: 'Boundary Conflict',
  NEEDS_REVIEW: 'Needs Review',
  READY_FOR_OCR: 'Ready for OCR',
  OCR_COMPLETE: 'OCR Complete',
  VERIFIED: 'Authoritative Verified',
  PROCESSING: 'Processing GIS',
  UPLOADED: 'Uploaded',
  EXTRACTED: 'Extracted',
  RESOLVED: 'Conflict Resolved',
  FAILED: 'Failed',
  COMING_NEXT: 'Predictive Model Pending',
  ACTIVE: 'Active Register',
  IN_REVIEW: 'In Review',
  PENDING: 'Pending Verification',
  PLANNED: 'Planned Corridor',
  UNDER_CONSTRUCTION: 'Under Construction',
  SURVEY_IN_PROGRESS: 'Survey In Progress',
}

export function Badge({ value }: { value: string }) {
  const normalized = value.toUpperCase()
  const tone =
    normalized === 'PASS' || normalized === 'VERIFIED' || normalized === 'ACTIVE' || normalized === 'OCR_COMPLETE'
      ? 'success'
      : normalized === 'CONFLICT' || normalized === 'FAILED'
      ? 'danger'
      : normalized === 'WARNING' || normalized === 'NEEDS_REVIEW' || normalized === 'IN_REVIEW' || normalized === 'SURVEY_IN_PROGRESS'
      ? 'warning'
      : 'neutral'

  return (
    <span className={`badge glow-badge badge-${tone}`}>
      <span className="badge-glow-dot" />
      <span>{labels[normalized] ?? value.replaceAll('_', ' ')}</span>
    </span>
  )
}

export function SeverityBadge({ value }: { value: Severity }) {
  return <Badge value={value} />
}
