import React, { useEffect, useState } from 'react'
import {
  AlertCircle,
  ArrowUpRight,
  Building2,
  CheckCircle2,
  FileCheck2,
  FileText,
  FolderKanban,
  Layers,
  MapPin,
  MapPinned,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  UploadCloud,
  X,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import './App.css'
import { Badge, SeverityBadge } from './components/Badge'
import { Layout, type View } from './components/Layout'
import { AuthProvider, useAuth } from './context/AuthContext'
import { api } from './services/api'
import type {
  DocumentRecord,
  DocumentType,
  HealthResponse,
  InfrastructureProject,
  ParcelRecord,
  ValidationResponse,
} from './types/api'

function formatArea(value: number | null | undefined) {
  return value == null
    ? '—'
    : `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })} m²`
}

function formatDate(value: string) {
  try {
    return new Intl.DateTimeFormat('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(new Date(value))
  } catch {
    return value
  }
}

function ErrorMessage({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="error-state">
      <AlertCircle size={20} className="flex-shrink-0" />
      <div>
        <strong>System Notice</strong>
        <p>{message}</p>
      </div>
      {onRetry && (
        <button className="button button-secondary ml-auto" onClick={onRetry}>
          <RefreshCw size={14} /> Retry
        </button>
      )}
    </div>
  )
}

function EmptyState({
  icon: Icon,
  title,
  message,
}: {
  icon: LucideIcon
  title: string
  message: string
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Icon size={24} />
      </div>
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  )
}

function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string
  title: string
  description: string
  action?: React.ReactNode
}) {
  return (
    <div className="page-header">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  )
}

/* ==========================================================================
   ROLE DUTY BANNERS
   ========================================================================== */
function RoleDutyBanner({
  onAction,
}: {
  onAction: (target: View) => void
}) {
  const { role, user } = useAuth()

  if (role === 'operator') {
    return (
      <div className="role-duty-banner operator-duty">
        <div className="banner-content">
          <div className="banner-icon-badge">
            <FileCheck2 size={22} className="text-emerald-300" />
          </div>
          <div className="banner-text">
            <strong>Operator Intake Desk · Active Jurisdiction</strong>
            <span>
              Logged in as {user.name} ({user.jurisdiction}). Primary workflow: Register source deeds,
              link cadastral records, and queue documents for human verification.
            </span>
          </div>
        </div>
        <button className="banner-action-btn" onClick={() => onAction('documents')}>
          <UploadCloud size={15} /> Open Intake Register
        </button>
      </div>
    )
  }

  if (role === 'tehsildar') {
    return (
      <div className="role-duty-banner tehsildar-duty">
        <div className="banner-content">
          <div className="banner-icon-badge">
            <ShieldCheck size={22} className="text-amber-300" />
          </div>
          <div className="banner-text">
            <strong>Revenue Magistrate Desk · Mulshi Sub-Division</strong>
            <span>
              Logged in as {user.name}. Authoritative GIS validation, cadastral Khasra review, and
              spatial overlap resolution active.
            </span>
          </div>
        </div>
        <button className="banner-action-btn" onClick={() => onAction('validation')}>
          <MapPin size={15} /> Launch Spatial Validator
        </button>
      </div>
    )
  }

  return (
    <div className="role-duty-banner director-duty">
      <div className="banner-content">
        <div className="banner-icon-badge">
          <Building2 size={22} className="text-indigo-300" />
        </div>
        <div className="banner-text">
          <strong>Executive Command · National Cadastral Board</strong>
          <span>
            Logged in as {user.name} (Commissioner). High-level corridor impact intelligence,
            infrastructure alignment reviews, and macro dispute tracking.
          </span>
        </div>
      </div>
      <button className="banner-action-btn" onClick={() => onAction('infrastructure')}>
        <Layers size={15} /> Inspect Corridors
      </button>
    </div>
  )
}

/* ==========================================================================
   PARCEL INSPECTION DRAWER
   ========================================================================== */
function ParcelDrawer({
  parcel,
  onClose,
  onValidate,
}: {
  parcel: ParcelRecord | null
  onClose: () => void
  onValidate: (parcel: ParcelRecord) => void
}) {
  if (!parcel) return null

  return (
    <div className="inspector-drawer-backdrop" onClick={onClose}>
      <aside className="inspector-drawer" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <span className="eyebrow">Authoritative Cadastre</span>
            <h2>Khasra {parcel.khasra_number}</h2>
            <p>
              {parcel.village}, {parcel.tehsil ?? parcel.district}, {parcel.state}
            </p>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close drawer">
            <X size={18} />
          </button>
        </div>

        <div className="drawer-section">
          <h3>Record Metadata</h3>
          <div className="meta-grid">
            <div className="meta-card">
              <span>Parcel ID</span>
              <strong className="mono">{parcel.id}</strong>
            </div>
            <div className="meta-card">
              <span>Khata Number</span>
              <strong>{parcel.khata_number ?? 'Not assigned'}</strong>
            </div>
            <div className="meta-card">
              <span>Recorded Area</span>
              <strong>{formatArea(parcel.recorded_area_m2)}</strong>
            </div>
            <div className="meta-card">
              <span>Spatial SRID</span>
              <strong>EPSG:{parcel.srid}</strong>
            </div>
            <div className="meta-card">
              <span>Record Status</span>
              <div>
                <Badge value={parcel.status} />
              </div>
            </div>
            <div className="meta-card">
              <span>Verification</span>
              <div>
                <Badge value={parcel.verification_status} />
              </div>
            </div>
          </div>
        </div>

        <div className="drawer-section">
          <h3>Spatial Boundary (GeoJSON)</h3>
          <p className="text-xs text-slate-400 mb-2">
            Deterministic 2D coordinates digitized from cadastral survey sheet:
          </p>
          <pre className="geojson-box">
            {JSON.stringify(parcel.geometry, null, 2)}
          </pre>
        </div>

        <div className="mt-auto pt-4 border-t border-white/10 flex gap-3">
          <button
            className="button button-primary flex-1"
            onClick={() => {
              onClose()
              onValidate(parcel)
            }}
          >
            <ShieldCheck size={16} /> Run GIS Validation
          </button>
          <button className="button button-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </aside>
    </div>
  )
}

/* ==========================================================================
   VIEW: OVERVIEW (HOME)
   ========================================================================== */
function Home({
  health,
  documents,
  parcels,
  infrastructure,
  onNavigate,
  onInspectParcel,
}: {
  health: HealthResponse | null
  documents: DocumentRecord[]
  parcels: ParcelRecord[]
  infrastructure: InfrastructureProject[]
  onNavigate: (view: View) => void
  onInspectParcel: (parcel: ParcelRecord) => void
}) {
  const { user } = useAuth()
  const reviewCount = parcels.filter(parcel => parcel.verification_status !== 'VERIFIED').length
  const verifiedCount = parcels.filter(parcel => parcel.verification_status === 'VERIFIED').length

  return (
    <>
      <PageHeader
        eyebrow="Operations intelligence"
        title={`Good day, ${user.name.split(' ')[0]}`}
        description="Unified portal for document intake, GIS cadastre verification, and infrastructure corridor intelligence."
        action={
          <div className="date-stamp">
            {new Intl.DateTimeFormat('en-IN', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            }).format(new Date())}
          </div>
        }
      />

      {/* Role Duty Banner */}
      <RoleDutyBanner onAction={onNavigate} />

      {/* Live Firestore / Backend Connectivity notice */}
      <div className="notice-banner">
        <div className="notice-icon">
          <CheckCircle2 size={20} />
        </div>
        <div>
          <strong>
            AUTHORITATIVE CLOUD CADASTRE &bull; {health?.status === 'ok' ? 'HEALTHY' : 'CONNECTED'}
          </strong>
          <span>
            {health
              ? `Database ${health.database}. Environment: ${health.environment}. Authorized officer session active.`
              : 'Connected to Firestore cadastre & local authorized records repository.'}
          </span>
        </div>
        <span className="notice-label">GOVT RECORD CLOUD</span>
      </div>

      {/* Stat Grid */}
      <div className="stat-grid">
        <button className="stat-card" onClick={() => onNavigate('documents')}>
          <span className="stat-icon blue">
            <FileCheck2 size={20} />
          </span>
          <span className="stat-label">Document Register</span>
          <strong>{documents.length}</strong>
          <small>Source records ingested</small>
          <ArrowUpRight className="stat-arrow" size={16} />
        </button>

        <button className="stat-card" onClick={() => onNavigate('parcels')}>
          <span className="stat-icon green">
            <MapPinned size={20} />
          </span>
          <span className="stat-label">Total Cadastral Parcels</span>
          <strong>{parcels.length}</strong>
          <small>{verifiedCount} verified &bull; {reviewCount} pending</small>
          <ArrowUpRight className="stat-arrow" size={16} />
        </button>

        <button className="stat-card" onClick={() => onNavigate('validation')}>
          <span className="stat-icon amber">
            <ShieldCheck size={20} />
          </span>
          <span className="stat-label">Spatial Review Queue</span>
          <strong>{reviewCount}</strong>
          <small>Awaiting Tehsildar sign-off</small>
          <ArrowUpRight className="stat-arrow" size={16} />
        </button>

        <button className="stat-card" onClick={() => onNavigate('infrastructure')}>
          <span className="stat-icon slate">
            <Building2 size={20} />
          </span>
          <span className="stat-label">Corridor Projects</span>
          <strong>{infrastructure.length}</strong>
          <small>Monitored public rights-of-way</small>
          <ArrowUpRight className="stat-arrow" size={16} />
        </button>
      </div>

      {/* Home Grid */}
      <div className="home-grid">
        {/* Left: Pending Document & Parcel Review Queue */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Priority Queue</span>
              <h2>Active Intake & Cadastre Records</h2>
            </div>
            <button className="text-button" onClick={() => onNavigate('parcels')}>
              View all parcels <ArrowUpRight size={14} />
            </button>
          </div>

          <div className="activity-list">
            {parcels.slice(0, 5).map(parcel => (
              <div
                className="activity-row cursor-pointer"
                key={parcel.id}
                onClick={() => onInspectParcel(parcel)}
                title="Click to inspect parcel"
              >
                <div className="file-type">KH</div>
                <div className="activity-copy">
                  <strong>Khasra {parcel.khasra_number} &bull; {parcel.village}</strong>
                  <span>
                    {parcel.district}, {parcel.state} &bull; {formatArea(parcel.recorded_area_m2)}
                  </span>
                </div>
                <Badge value={parcel.verification_status} />
              </div>
            ))}
          </div>
        </section>

        {/* Right: Operational Guidance */}
        <section className="panel guidance-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Verification Protocol</span>
              <h2>Determinism Over Speculation</h2>
            </div>
            <ShieldCheck size={20} className="text-emerald-400" />
          </div>

          <p>
            BhuDhrishti strictly enforces <strong>deterministic geometric validation</strong>.
            Polygon intersection, area discrepancy, and overlapping boundaries are computed using
            exact spatial math rather than opaque speculative AI models.
          </p>

          <div className="workflow-line">
            <span className="done">1</span>
            <span>Deed Intake</span>
            <i />
            <span className="done">2</span>
            <span>Spatial Align</span>
            <i />
            <span className="done">3</span>
            <span>Magistrate Sign</span>
          </div>

          <div className="flex gap-3 px-6">
            <button
              className="button button-primary flex-1"
              onClick={() => onNavigate('documents')}
            >
              <UploadCloud size={16} /> Upload Record
            </button>
            <button
              className="button button-secondary flex-1"
              onClick={() => onNavigate('validation')}
            >
              <MapPin size={16} /> GIS Checks
            </button>
          </div>
        </section>
      </div>
    </>
  )
}

/* ==========================================================================
   VIEW: DOCUMENTS REGISTER (OPERATOR DESK)
   ========================================================================== */
function Documents({
  documents,
  parcels,
  onRefresh,
  setMessage,
}: {
  documents: DocumentRecord[]
  parcels: ParcelRecord[]
  onRefresh: () => void
  setMessage: (message: string) => void
}) {
  const [file, setFile] = useState<File | null>(null)
  const [parcelId, setParcelId] = useState('')
  const [documentType, setDocumentType] = useState<DocumentType>('LAND_DEED')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<string | null>(null)
  const [assignParcel, setAssignParcel] = useState('')

  async function upload() {
    if (!file) return setError('Choose a valid document (PDF, JPEG, PNG) first.')
    setBusy(true)
    setError('')
    try {
      await api.uploadDocument(file, parcelId, documentType)
      setFile(null)
      setParcelId('')
      setMessage(`Document "${file.name}" uploaded successfully and registered for OCR review.`)
      onRefresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Upload failed.')
    } finally {
      setBusy(false)
    }
  }

  async function assign(document: DocumentRecord) {
    setBusy(true)
    setError('')
    try {
      await api.associateDocument(document.id, assignParcel || null)
      setMessage(
        assignParcel
          ? `Document successfully linked to parcel ${assignParcel}.`
          : 'Document unlinked from parcel.'
      )
      setSelected(null)
      onRefresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Association failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Operator intake workspace"
        title="Document Register"
        description="Upload official deeds, mutation records, and survey maps. Link every source document to its corresponding cadastral parcel."
        action={
          <label className="button button-primary upload-label">
            <UploadCloud size={16} /> Choose Document
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
              onChange={event => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
        }
      />

      {error && <ErrorMessage message={error} />}

      {/* Upload Strip */}
      <section className="upload-strip">
        <div className="upload-drop">
          <UploadCloud size={24} />
          <div>
            <strong>{file ? file.name : 'Select or drop an authorized land record'}</strong>
            <span>
              {file
                ? `${(file.size / 1024).toFixed(1)} KB &bull; Click 'Register Record' to submit`
                : 'PDF, JPEG, or PNG &bull; Direct offline-first client storage & Firestore sync'}
            </span>
          </div>
        </div>

        <div className="form-inline">
          <select
            value={documentType}
            onChange={event => setDocumentType(event.target.value as DocumentType)}
            aria-label="Document type"
          >
            <option value="LAND_DEED">Land Deed (Bhu Patra)</option>
            <option value="SALE_DEED">Sale Deed (Vikraya Patra)</option>
            <option value="KHATA">Khata Extract</option>
            <option value="KHASRA">Khasra Record</option>
            <option value="SURVEY_MAP">Cadastral Survey Map</option>
            <option value="LAND_RECORD">General Revenue Record</option>
          </select>

          <select
            value={parcelId}
            onChange={event => setParcelId(event.target.value)}
            aria-label="Associate parcel"
          >
            <option value="">No parcel link (unassigned)</option>
            {parcels.map(parcel => (
              <option key={parcel.id} value={parcel.id}>
                Khasra {parcel.khasra_number} &bull; {parcel.village} ({parcel.id})
              </option>
            ))}
          </select>

          <button
            className="button button-primary"
            onClick={upload}
            disabled={busy || !file}
          >
            {busy ? 'Registering…' : 'Register Record'}
          </button>
        </div>
      </section>

      {/* Document Table */}
      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Authoritative Records</span>
            <h2>
              Ingested Documents <span className="count-pill">{documents.length}</span>
            </h2>
          </div>
          <button className="glass-icon-btn" onClick={onRefresh} aria-label="Refresh documents">
            <RefreshCw size={16} />
          </button>
        </div>

        {documents.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No documents in register"
            message="Upload the first deed or revenue record to begin intake."
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Document Name</th>
                  <th>Classification</th>
                  <th>Linked Parcel</th>
                  <th>Processing State</th>
                  <th>Date Ingested</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {documents.map(document => (
                  <tr key={document.id}>
                    <td>
                      <div className="table-file">
                        <div className="file-type small">
                          {document.original_filename.split('.').pop()?.toUpperCase() ?? 'DOC'}
                        </div>
                        <div>
                          <strong>{document.original_filename}</strong>
                          <span>{Math.round(document.file_size_bytes / 1024)} KB</span>
                        </div>
                      </div>
                    </td>
                    <td>{document.document_type.replaceAll('_', ' ')}</td>
                    <td>
                      {document.parcel_id ? (
                        <span className="mono text-teal-300">{document.parcel_id}</span>
                      ) : (
                        <span className="muted">Unassigned</span>
                      )}
                    </td>
                    <td>
                      <Badge value={document.status} />
                    </td>
                    <td>{formatDate(document.created_at)}</td>
                    <td>
                      <button
                        className="link-button"
                        onClick={() => {
                          setSelected(document.id)
                          setAssignParcel(document.parcel_id ?? '')
                        }}
                      >
                        {selected === document.id ? 'Editing…' : 'Manage Link'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Parcel Association Drawer/Inline Box */}
        {selected && (
          <div className="assignment-editor">
            <div>
              <strong>Reassign or Detach Parcel</strong>
              <span>Update the spatial cadastre linkage for this document.</span>
            </div>
            <select
              value={assignParcel}
              onChange={event => setAssignParcel(event.target.value)}
            >
              <option value="">No parcel association (Unlinked)</option>
              {parcels.map(parcel => (
                <option key={parcel.id} value={parcel.id}>
                  Khasra {parcel.khasra_number} &bull; {parcel.village}
                </option>
              ))}
            </select>
            <button
              className="button button-primary"
              onClick={() => {
                const doc = documents.find(item => item.id === selected)
                if (doc) void assign(doc)
              }}
              disabled={busy}
            >
              Save Linkage
            </button>
            <button className="button button-secondary" onClick={() => setSelected(null)}>
              Cancel
            </button>
          </div>
        )}
      </section>

      <section className="future-card">
        <div className="future-icon">
          <FileCheck2 size={22} />
        </div>
        <div>
          <span className="eyebrow">Human-in-the-Loop OCR</span>
          <h2>Deterministic Extraction Workspace</h2>
          <p>
            When documents reach OCR completion, side-by-side text comparisons and field diffs will
            be presented for operator verification. Unverified values are never fabricated.
          </p>
        </div>
        <Badge value="COMING_NEXT" />
      </section>
    </>
  )
}

/* ==========================================================================
   VIEW: PARCELS REGISTER (TEHSILDAR DESK)
   ========================================================================== */
function Parcels({
  parcels,
  onRefresh,
  onSelect,
  onInspect,
}: {
  parcels: ParcelRecord[]
  onRefresh: (search?: string) => Promise<void>
  onSelect: (parcel: ParcelRecord) => void
  onInspect: (parcel: ParcelRecord) => void
}) {
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSearch() {
    setLoading(true)
    setError('')
    try {
      await onRefresh(search)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Search failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Tehsildar cadastre register"
        title="Authoritative Parcels"
        description="Search and inspect cadastral plots across villages, Khasra identifiers, and khatas. Access geometry coordinates and trigger GIS checks."
        action={
          <button className="button button-secondary" onClick={() => void onRefresh()}>
            <RefreshCw size={15} /> Refresh Cadastre
          </button>
        }
      />

      {error && <ErrorMessage message={error} />}

      {/* Search Bar */}
      <section className="filter-bar">
        <div className="search-field">
          <Search size={18} />
          <input
            value={search}
            onChange={event => setSearch(event.target.value)}
            onKeyDown={event => {
              if (event.key === 'Enter') void handleSearch()
            }}
            placeholder="Search Khasra number, Khata, village, or parcel ID..."
          />
          <button onClick={() => void handleSearch()}>
            {loading ? 'Searching…' : 'Filter'}
          </button>
        </div>
        <span className="result-count">{parcels.length} parcels in registry</span>
      </section>

      {/* Parcel Table */}
      <section className="panel table-panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Khasra / ID</th>
                <th>Location</th>
                <th>Khata #</th>
                <th>Recorded Area</th>
                <th>Record Status</th>
                <th>Verification</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {parcels.map(parcel => (
                <tr key={parcel.id}>
                  <td>
                    <div>
                      <strong className="text-white">Khasra {parcel.khasra_number}</strong>
                      <span className="mono">{parcel.id}</span>
                    </div>
                  </td>
                  <td>
                    <strong>{parcel.village}</strong>
                    <span className="sub-cell">
                      {[parcel.tehsil, parcel.district, parcel.state].filter(Boolean).join(' &bull; ')}
                    </span>
                  </td>
                  <td>
                    {parcel.khata_number ? (
                      <span>Khata {parcel.khata_number}</span>
                    ) : (
                      <span className="muted">Not recorded</span>
                    )}
                  </td>
                  <td>{formatArea(parcel.recorded_area_m2)}</td>
                  <td>
                    <Badge value={parcel.status} />
                  </td>
                  <td>
                    <Badge value={parcel.verification_status} />
                  </td>
                  <td>
                    <div className="flex gap-2">
                      <button
                        className="button button-secondary text-xs px-2.5 py-1 min-h-0"
                        onClick={() => onInspect(parcel)}
                      >
                        Inspect
                      </button>
                      <button
                        className="button button-primary text-xs px-2.5 py-1 min-h-0"
                        onClick={() => onSelect(parcel)}
                      >
                        Validate GIS
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {parcels.length === 0 && (
          <EmptyState
            icon={MapPinned}
            title="No cadastral parcels found"
            message="Try a broader search query or reset the search filter."
          />
        )}
      </section>
    </>
  )
}

/* ==========================================================================
   VIEW: GIS VALIDATION (TEHSILDAR SPATIAL VALIDATOR)
   ========================================================================== */
function Validation({
  selectedParcel,
  validation,
  onRun,
  loading,
  error,
  onSelectParcel,
}: {
  selectedParcel: ParcelRecord | null
  validation: ValidationResponse | null
  onRun: () => void
  loading: boolean
  error: string
  onSelectParcel: () => void
}) {
  return (
    <>
      <PageHeader
        eyebrow="Revenue magistrate spatial check"
        title="GIS Spatial Validation"
        description="Run deterministic geometry, polygon self-intersection, area comparison, and cadastral overlap checks against authoritative parcel boundaries."
        action={
          <button
            className="button button-primary"
            onClick={onRun}
            disabled={!selectedParcel || loading}
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="animate-spin" /> Running Spatial Checks…
              </>
            ) : (
              <>
                <ShieldCheck size={16} /> Run GIS Checks
              </>
            )}
          </button>
        }
      />

      {error && <ErrorMessage message={error} />}

      {!selectedParcel ? (
        <section className="selection-empty">
          <div className="empty-icon">
            <MapPinned size={26} />
          </div>
          <h2>Select a parcel from cadastre</h2>
          <p>
            Choose any cadastral parcel from the register to compute its geometry validity, area
            difference ratio, and detect overlapping boundaries.
          </p>
          <button className="button button-primary" onClick={onSelectParcel}>
            <FolderKanban size={16} /> Open Parcel Register
          </button>
        </section>
      ) : (
        <>
          {/* Selected Record Card */}
          <div className="selected-record">
            <div className="record-symbol">
              <MapPinned size={20} />
            </div>
            <div>
              <span className="eyebrow">Active Target Parcel</span>
              <strong>
                Khasra {selectedParcel.khasra_number} &bull; {selectedParcel.village}
              </strong>
              <span>
                {selectedParcel.id} &bull; {selectedParcel.district}, {selectedParcel.state} &bull;{' '}
                Recorded: {formatArea(selectedParcel.recorded_area_m2)}
              </span>
            </div>
            <Badge value={selectedParcel.verification_status} />
          </div>

          {validation ? (
            <>
              {/* Validation Summary */}
              <div className="validation-summary">
                <div>
                  <span className="eyebrow">Authoritative Spatial Result</span>
                  <h2>{validation.summary}</h2>
                  <p>
                    Deterministic polygon analysis returned by the backend GIS service. Zero
                    hallucinated scores.
                  </p>
                </div>
                <SeverityBadge value={validation.overall_severity} />
              </div>

              {/* Validation Metrics */}
              <div className="validation-metrics">
                <div className="metric">
                  <span>Geometry Validity</span>
                  <strong
                    className={validation.geometry_valid ? 'metric-success' : 'metric-danger'}
                  >
                    {validation.geometry_valid ? 'Valid Polygon' : 'Invalid Geometry'}
                  </strong>
                </div>

                <div className="metric">
                  <span>Calculated GIS Area</span>
                  <strong>{formatArea(validation.calculated_area_m2)}</strong>
                </div>

                <div className="metric">
                  <span>Area Discrepancy</span>
                  <strong
                    className={
                      validation.area_difference_percent && validation.area_difference_percent > 10
                        ? 'metric-warning'
                        : 'metric-success'
                    }
                  >
                    {validation.area_difference_percent == null
                      ? '—'
                      : `${validation.area_difference_percent.toFixed(1)}%`}
                  </strong>
                </div>

                <div className="metric">
                  <span>Boundary Overlaps</span>
                  <strong
                    className={validation.overlap_detected ? 'metric-danger' : 'metric-success'}
                  >
                    {validation.overlap_detected
                      ? `${validation.overlapping_parcel_ids.length} Overlapping`
                      : 'None Detected'}
                  </strong>
                </div>
              </div>

              {/* Deterministic Findings Panel */}
              <section className="panel findings-panel">
                <div className="panel-heading">
                  <div>
                    <span className="eyebrow">Geometric Proofs</span>
                    <h2>Validation Findings</h2>
                  </div>
                  <span className="muted">{validation.findings.length} findings logged</span>
                </div>

                <div className="finding-list">
                  {validation.findings.map(finding => (
                    <div className="finding-row" key={finding.code}>
                      <SeverityBadge value={finding.severity} />
                      <div>
                        <strong>{finding.code.replaceAll('_', ' ')}</strong>
                        <p>{finding.message}</p>
                      </div>
                      {finding.intersection_percentage != null && (
                        <span className="finding-value">
                          {finding.intersection_percentage.toFixed(1)}% spatial impact
                        </span>
                      )}
                    </div>
                  ))}
                </div>

                {validation.overlap_results.length > 0 && (
                  <div className="overlap-note">
                    <strong>Identified Overlapping Cadastral Plots</strong>
                    {validation.overlap_results.map(overlap => (
                      <span key={overlap.parcel_id}>
                        {overlap.parcel_id} &bull; {overlap.overlap_percentage.toFixed(1)}% overlap (
                        {formatArea(overlap.overlap_area_m2)})
                      </span>
                    ))}
                  </div>
                )}
              </section>
            </>
          ) : (
            <section className="selection-empty compact">
              <ShieldCheck size={28} className="text-teal-400" />
              <h2>Parcel Ready for Spatial Validation</h2>
              <p>
                Click "Run GIS Checks" in the top-right header to initiate deterministic geometry
                and overlap calculation.
              </p>
            </section>
          )}
        </>
      )}
    </>
  )
}

/* ==========================================================================
   VIEW: INFRASTRUCTURE RISK (DIRECTOR EXECUTIVE SUITE)
   ========================================================================== */
function Infrastructure({
  projects,
  loading,
  error,
  onRefresh,
}: {
  projects: InfrastructureProject[]
  loading: boolean
  error: string
  onRefresh: () => void
}) {
  return (
    <>
      <PageHeader
        eyebrow="Director executive suite"
        title="Infrastructure Corridors"
        description="Monitor national infrastructure alignments (expressways, rail corridors, pipelines) and oversee spatial right-of-way conflict clearances."
        action={
          <button className="button button-secondary" onClick={onRefresh}>
            <RefreshCw size={15} /> Refresh Corridors
          </button>
        }
      />

      {error && <ErrorMessage message={error} />}

      {/* Orbit Graphic Hero */}
      <section className="future-hero">
        <div className="future-hero-copy">
          <span className="eyebrow">National Land Intelligence</span>
          <h2>Macro Alignment & Right-of-Way Dispute Intelligence</h2>
          <p>
            Public corridors require authoritative overlay against digitized village cadastres.
            BhuDhrishti enables proactive corridor conflict resolution without opaque estimation.
          </p>
          <div className="future-points">
            <span>
              <CheckCircle2 size={15} className="text-teal-300" /> Authorized Corridor Register
            </span>
            <span>
              <CheckCircle2 size={15} className="text-teal-300" /> Linear Coordinate LineStrings
            </span>
            <span>
              <span className="pending-dot" /> Predictive Risk Intelligence Layer Pending
            </span>
          </div>
        </div>

        <div className="future-orbit">
          <div className="orbit-center">
            <ShieldAlert size={20} />
            <span>RISK</span>
          </div>
          <div className="orbit-ring ring-one" />
          <div className="orbit-ring ring-two" />
        </div>
      </section>

      {/* Infrastructure Project Table */}
      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Authoritative Registry</span>
            <h2>
              Infrastructure Projects <span className="count-pill">{projects.length}</span>
            </h2>
          </div>
          {loading && <span className="muted">Synchronizing…</span>}
        </div>

        {projects.length === 0 ? (
          <EmptyState
            icon={Building2}
            title="No infrastructure corridors"
            message="Public project corridors will appear here once entered in the national register."
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Project Name / ID</th>
                  <th>Corridor Type</th>
                  <th>Execution Status</th>
                  <th>Spatial SRID</th>
                  <th>Risk Layer</th>
                </tr>
              </thead>
              <tbody>
                {projects.map(project => (
                  <tr key={project.id}>
                    <td>
                      <strong>{project.name}</strong>
                      <span className="mono">{project.id}</span>
                    </td>
                    <td>{project.project_type.replaceAll('_', ' ')}</td>
                    <td>
                      <Badge value={project.status} />
                    </td>
                    <td>EPSG:{project.srid}</td>
                    <td>
                      <Badge value="COMING_NEXT" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}

/* ==========================================================================
   APP MAIN CONTROLLER
   ========================================================================== */
function AppContent() {
  const [view, setView] = useState<View>('home')
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [parcels, setParcels] = useState<ParcelRecord[]>([])
  const [infrastructure, setInfrastructure] = useState<InfrastructureProject[]>([])
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [selectedParcel, setSelectedParcel] = useState<ParcelRecord | null>(null)
  const [inspectingParcel, setInspectingParcel] = useState<ParcelRecord | null>(null)
  const [validation, setValidation] = useState<ValidationResponse | null>(null)
  const [validationError, setValidationError] = useState('')
  const [validationLoading, setValidationLoading] = useState(false)
  const [globalError, setGlobalError] = useState('')
  const [message, setMessage] = useState('')

  async function loadDocuments() {
    try {
      setDocuments(await api.listDocuments())
      setGlobalError('')
    } catch (reason) {
      setGlobalError(reason instanceof Error ? reason.message : 'Documents unavailable.')
    }
  }

  async function loadParcels(search = '') {
    try {
      const result = await api.listParcels(search)
      setParcels(result.items)
      if (selectedParcel) {
        setSelectedParcel(
          result.items.find(parcel => parcel.id === selectedParcel.id) ?? selectedParcel
        )
      }
    } catch (reason) {
      setGlobalError(reason instanceof Error ? reason.message : 'Parcels unavailable.')
    }
  }

  async function loadInfrastructure() {
    try {
      setInfrastructure(await api.listInfrastructure())
    } catch (reason) {
      setGlobalError(reason instanceof Error ? reason.message : 'Infrastructure unavailable.')
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void Promise.all([
        api.getHealth().then(setHealth).catch(() => setHealth(null)),
        loadDocuments(),
        loadParcels(),
        loadInfrastructure(),
      ])
    }, 0)
    return () => window.clearTimeout(timer)
  }, [])

  async function runValidation(targetParcel?: ParcelRecord) {
    const parcelToValidate = targetParcel ?? selectedParcel
    if (!parcelToValidate) return
    setValidationLoading(true)
    setValidationError('')
    try {
      const res = await api.validateParcel(parcelToValidate.id)
      setValidation(res)
    } catch (reason) {
      setValidationError(reason instanceof Error ? reason.message : 'Validation failed.')
    } finally {
      setValidationLoading(false)
    }
  }

  function handleSelectAndValidate(parcel: ParcelRecord) {
    setSelectedParcel(parcel)
    setValidation(null)
    setView('validation')
    void runValidation(parcel)
  }

  function navigate(nextView: View) {
    setView(nextView)
    setMessage('')
  }

  return (
    <Layout view={view} onNavigate={navigate}>
      {message && (
        <div className="global-toast">
          <CheckCircle2 size={18} /> {message}
          <button onClick={() => setMessage('')} aria-label="Dismiss message">
            &times;
          </button>
        </div>
      )}

      {globalError && (
        <ErrorMessage
          message={globalError}
          onRetry={() => {
            void loadDocuments()
            void loadParcels()
            void loadInfrastructure()
          }}
        />
      )}

      {/* Parcel Inspector Drawer */}
      <ParcelDrawer
        parcel={inspectingParcel}
        onClose={() => setInspectingParcel(null)}
        onValidate={parcel => handleSelectAndValidate(parcel)}
      />

      {view === 'home' && (
        <Home
          health={health}
          documents={documents}
          parcels={parcels}
          infrastructure={infrastructure}
          onNavigate={navigate}
          onInspectParcel={parcel => setInspectingParcel(parcel)}
        />
      )}

      {view === 'documents' && (
        <Documents
          documents={documents}
          parcels={parcels}
          onRefresh={() => void loadDocuments()}
          setMessage={setMessage}
        />
      )}

      {view === 'parcels' && (
        <Parcels
          parcels={parcels}
          onRefresh={search => loadParcels(search)}
          onSelect={parcel => handleSelectAndValidate(parcel)}
          onInspect={parcel => setInspectingParcel(parcel)}
        />
      )}

      {view === 'validation' && (
        <Validation
          selectedParcel={selectedParcel}
          validation={validation}
          onRun={() => void runValidation()}
          loading={validationLoading}
          error={validationError}
          onSelectParcel={() => setView('parcels')}
        />
      )}

      {view === 'infrastructure' && (
        <Infrastructure
          projects={infrastructure}
          loading={false}
          error={globalError}
          onRefresh={() => void loadInfrastructure()}
        />
      )}
    </Layout>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}