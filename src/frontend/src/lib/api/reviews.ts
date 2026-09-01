import { request } from './client'
import type { AuthUser } from './types'

export type PlaceReview = {
  id: string
  workspace_id: string
  location_name: string
  rating: number
  review_text: string | null
  created_by: string
  created_at: string
  user?: AuthUser
}

export const reviewsApi = {
  submitReview: (workspaceId: string, payload: { location_name: string; rating: number; review_text?: string }) => {
    return request<PlaceReview>(`/api/v1/workspaces/${workspaceId}/reviews`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  listReviews: (workspaceId: string) => {
    return request<PlaceReview[]>(`/api/v1/workspaces/${workspaceId}/reviews`)
  }
}
