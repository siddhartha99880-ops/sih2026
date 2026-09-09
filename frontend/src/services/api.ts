import type { DocumentRecord, DocumentStatus, DocumentType, HealthResponse, InfrastructureProject, ParcelListResponse, ValidationResponse } from '../types/api'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1').replace(/\/$/, '')

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const payload = await response.json() as { detail?: string; error?: { message?: string } }
      message = payload.detail ?? payload.error?.message ?? message
    } catch {
      // Keep the HTTP status when the server does not return JSON.
    }
    throw new Error(message)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  getHealth: () => request<HealthResponse>('/health'),
  listDocuments: () => request<DocumentRecord[]>('/documents'),
  uploadDocument: (file: File, parcelId: string, documentType: DocumentType) => {
    const form = new FormData()
    form.append('file', file)
    if (parcelId) form.append('parcel_id', parcelId)
    form.append('document_type', documentType)
    return request<DocumentRecord>('/documents', { method: 'POST', body: form })
  },
  associateDocument: (documentId: string, parcelId: string | null) => request<DocumentRecord>(`/documents/${documentId}/parcel`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ parcel_id: parcelId || null }),
  }),
  transitionDocument: (documentId: string, status: DocumentStatus) => request<DocumentRecord>(`/documents/${documentId}/status`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }),
  }),
  listParcels: (search: string) => request<ParcelListResponse>(`/parcels?limit=50${search ? `&search=${encodeURIComponent(search)}` : ''}`),
  validateParcel: (parcelId: string) => request<ValidationResponse>(`/validation/parcel/${parcelId}`, { method: 'POST' }),
  listInfrastructure: () => request<InfrastructureProject[]>('/infrastructure'),
}