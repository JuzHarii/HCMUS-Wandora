import { request } from './client'
import type { 
  Workspace, 
  CreateWorkspaceInput, 
  ItineraryPreview, 
  Itinerary, 
  TripOverview, 
  ItineraryVersion 
} from './types'

export const workspacesApi = {
  createWorkspace: (payload: CreateWorkspaceInput) => {
    return request<Workspace>("/api/v1/workspaces", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  },

  listWorkspaces: () => {
    return request<Workspace[]>('/api/v1/workspaces')
  },
  
  getWorkspace: (workspaceId: string) => {
    return request<Workspace>(`/api/v1/workspaces/${workspaceId}`)
  },

  getTripOverview: (workspaceId: string) => {
    return request<TripOverview>(`/api/v1/workspaces/${workspaceId}/overview`)
  },

  previewItinerary: (payload: CreateWorkspaceInput) => {
    return request<ItineraryPreview>('/api/v1/workspaces/preview-itinerary', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  generateItinerary: (workspaceId: string) => {
    return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/generate-itinerary`, {
      method: "POST",
      body: JSON.stringify({ force_regenerate: true }),
    })
  },

  initializeBlankItinerary: (workspaceId: string) => {
    return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/initialize-blank-itinerary`, {
      method: 'POST',
    })
  },

  getItinerary: (workspaceId: string) => {
    return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/itinerary`)
  },

  saveItineraryDraft: (workspaceId: string, preview: ItineraryPreview) => {
    return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/save-itinerary`, {
      method: 'POST',
      body: JSON.stringify({ source: preview.source, draft: preview.draft }),
    })
  },

  listItineraryVersions: (workspaceId: string) => {
    return request<ItineraryVersion[]>(`/api/v1/workspaces/${workspaceId}/itinerary-versions`)
  },

  restoreItineraryVersion: (workspaceId: string, versionId: string) => {
    return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/itinerary-versions/${versionId}/restore`, {
      method: 'POST',
    })
  },
  
  adjustItinerary: (workspaceId: string, payload: { prompt: string }) => {
    return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/adjust-itinerary`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }
}
