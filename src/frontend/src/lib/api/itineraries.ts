import { request } from './client'
import type { Activity, CreateActivityInput, Itinerary } from './types'

export const itinerariesApi = {
  getItinerary: (workspaceId: string) => {
    return request<Itinerary>(`/api/v1/itineraries/${workspaceId}`)
  },

  addActivity: (payload: CreateActivityInput) => {
    return request<Activity>('/api/v1/itineraries/activities', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  updateActivity: (activityId: string, payload: Partial<CreateActivityInput>) => {
    return request<Activity>(`/api/v1/itineraries/activities/${activityId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  }
}
