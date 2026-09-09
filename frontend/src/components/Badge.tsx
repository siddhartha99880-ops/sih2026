import type { Severity } from '../types/api'

const labels: Record<string, string> = { PASS: 'Pass', WARNING: 'Warning', CONFLICT: 'Conflict', NEEDS_REVIEW: 'Needs review', READY_FOR_OCR: 'Ready for OCR', VERIFIED: 'Verified', PROCESSING: 'Processing', UPLOADED: 'Uploaded', EXTRACTED: 'Extracted', RESOLVED: 'Resolved', FAILED: 'Failed' }

export function Badge({ value }: { value: string }) {
  const tone = value === 'PASS' || value === 'VERIFIED' ? 'success' : value === 'CONFLICT' || value === 'FAILED' ? 'danger' : value === 'WARNING' || value === 'NEEDS_REVIEW' ? 'warning' : 'neutral'
  return <span className={`badge badge-${tone}`}>{labels[value] ?? value.replaceAll('_', ' ')}</span>
}

export function SeverityBadge({ value }: { value: Severity }) { return <Badge value={value} /> }