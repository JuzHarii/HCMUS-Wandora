import { request } from './client'
import type { CreateWorkspaceInput, Workspace } from './types'

export type CheckDuplicateResponse = {
  has_duplicate: boolean
  duplicate_destination: boolean
}

export type VersionSummary = {
  version_number: number
  created_at: string
  generation_source: string | null
}

export const tripsApi = {
  checkDuplicates: (payload: CreateWorkspaceInput) => {
    return request<CheckDuplicateResponse>('/api/v1/trips/check-duplicates', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  getHistory: () => {
    return request<Workspace[]>('/api/v1/trips/history')
  },

  listVersions: (tripId: string) => {
    return request<VersionSummary[]>(`/api/v1/trips/${tripId}/versions`)
  },

  restoreVersion: (tripId: string, versionNumber: number) => {
    return request<Workspace>(`/api/v1/trips/${tripId}/versions/${versionNumber}/restore`, {
      method: 'POST'
    })
  }
}
