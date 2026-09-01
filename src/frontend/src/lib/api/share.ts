import { request } from './client'
import type { Itinerary } from './types'

export type ShareToken = {
  token: string
  workspace_id: string
  access_level: string
  expires_at: string | null
}

export type TripExport = {
  workspace_id: string
  format: string
  download_url: string
}

export const shareApi = {
  createShareLink: (workspaceId: string, payload: { access_level: string; expires_in_days?: number }) => {
    return request<ShareToken>(`/api/v1/workspaces/${workspaceId}/share`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  getSharedItinerary: (token: string) => {
    return request<Itinerary>(`/api/v1/share/${token}`)
  },

  exportTrip: (workspaceId: string, format: string = 'json') => {
    return request<TripExport>(`/api/v1/workspaces/${workspaceId}/export?format=${format}`)
  }
}
