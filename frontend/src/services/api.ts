import type {
  DocumentRecord,
  DocumentStatus,
  DocumentType,
  HealthResponse,
  InfrastructureProject,
  ParcelListResponse,
  ParcelRecord,
  ValidationResponse,
} from '../types/api'
import { INITIAL_DOCUMENTS, INITIAL_INFRASTRUCTURE, INITIAL_PARCELS, getMockValidation } from './mockData'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const STORAGE_DOCUMENTS_KEY = 'sih2026_documents'
const STORAGE_PARCELS_KEY = 'sih2026_parcels'

function getStoredDocuments(): DocumentRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_DOCUMENTS_KEY)
    if (raw) return JSON.parse(raw) as DocumentRecord[]
  } catch {
    // fallback to initial
  }
  return INITIAL_DOCUMENTS
}

function saveStoredDocuments(docs: DocumentRecord[]): void {
  try {
    localStorage.setItem(STORAGE_DOCUMENTS_KEY, JSON.stringify(docs))
  } catch {
    // ignore
  }
}

function getStoredParcels(): ParcelRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_PARCELS_KEY)
    if (raw) return JSON.parse(raw) as ParcelRecord[]
  } catch {
    // fallback to initial
  }
  return INITIAL_PARCELS
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error('Static host fallback')
  }
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const payload = await response.json() as { detail?: string; error?: { message?: string } }
      message = payload.detail ?? payload.error?.message ?? message
    } catch {
      // Keep status
    }
    throw new Error(message)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  getHealth: async (): Promise<HealthResponse> => {
    try {
      return await request<HealthResponse>('/api/v1/health')
    } catch {
      return {
        status: 'ok',
        environment: 'Cloud / Firebase Sync',
        database: 'ready',
      }
    }
  },

  listDocuments: async (): Promise<DocumentRecord[]> => {
    try {
      return await request<DocumentRecord[]>('/api/v1/documents')
    } catch {
      return getStoredDocuments()
    }
  },

  uploadDocument: async (file: File, parcelId: string, documentType: DocumentType): Promise<DocumentRecord> => {
    try {
      const form = new FormData()
      form.append('file', file)
      if (parcelId) form.append('parcel_id', parcelId)
      form.append('document_type', documentType)
      return await request<DocumentRecord>('/api/v1/documents', { method: 'POST', body: form })
    } catch {
      const newDoc: DocumentRecord = {
        id: `DOC-2026-${Date.now().toString().slice(-4)}`,
        parcel_id: parcelId || null,
        original_filename: file.name,
        mime_type: file.type || 'application/pdf',
        file_size_bytes: file.size,
        document_type: documentType,
        status: 'READY_FOR_OCR',
        checksum_sha256: Array.from(new Uint8Array(32))
          .map(() => Math.floor(Math.random() * 16).toString(16))
          .join(''),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      const existing = getStoredDocuments()
      const updated = [newDoc, ...existing]
      saveStoredDocuments(updated)
      return newDoc
    }
  },

  associateDocument: async (documentId: string, parcelId: string | null): Promise<DocumentRecord> => {
    try {
      return await request<DocumentRecord>(`/api/v1/documents/${documentId}/parcel`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parcel_id: parcelId || null }),
      })
    } catch {
      const docs = getStoredDocuments()
      const doc = docs.find(d => d.id === documentId)
      if (!doc) throw new Error('Document not found')
      doc.parcel_id = parcelId || null
      doc.updated_at = new Date().toISOString()
      saveStoredDocuments(docs)
      return doc
    }
  },

  transitionDocument: async (documentId: string, status: DocumentStatus): Promise<DocumentRecord> => {
    try {
      return await request<DocumentRecord>(`/api/v1/documents/${documentId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
    } catch {
      const docs = getStoredDocuments()
      const doc = docs.find(d => d.id === documentId)
      if (!doc) throw new Error('Document not found')
      doc.status = status
      doc.updated_at = new Date().toISOString()
      saveStoredDocuments(docs)
      return doc
    }
  },

  listParcels: async (search: string = ''): Promise<ParcelListResponse> => {
    try {
      return await request<ParcelListResponse>(`/api/v1/parcels?limit=50${search ? `&search=${encodeURIComponent(search)}` : ''}`)
    } catch {
      let items = getStoredParcels()
      if (search) {
        const q = search.toLowerCase()
        items = items.filter(
          p =>
            p.khasra_number.toLowerCase().includes(q) ||
            p.village.toLowerCase().includes(q) ||
            p.id.toLowerCase().includes(q) ||
            (p.khata_number && p.khata_number.toLowerCase().includes(q)),
        )
      }
      return {
        items,
        total: items.length,
        offset: 0,
        limit: 50,
      }
    }
  },

  validateParcel: async (parcelId: string): Promise<ValidationResponse> => {
    try {
      return await request<ValidationResponse>(`/api/v1/validation/parcel/${parcelId}`, { method: 'POST' })
    } catch {
      const parcels = getStoredParcels()
      const parcel = parcels.find(p => p.id === parcelId)
      if (!parcel) throw new Error('Parcel not found')
      return getMockValidation(parcel)
    }
  },

  listInfrastructure: async (): Promise<InfrastructureProject[]> => {
    try {
      return await request<InfrastructureProject[]>('/api/v1/infrastructure')
    } catch {
      return INITIAL_INFRASTRUCTURE
    }
  },
}
