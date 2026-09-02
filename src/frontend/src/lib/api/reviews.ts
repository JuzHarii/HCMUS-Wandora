import { request } from './client'

export type PlaceReview = {
  id: string
  workspace_id: string
  place_name: string
  rating: number
  comment: string | null
  user_id: string
  user_email: string | null
  user_full_name: string | null
  created_at: string
}

export const reviewsApi = {
  submitReview: (workspaceId: string, payload: { place_name: string; rating: number; comment?: string }) => {
    return request<PlaceReview>(`/api/v1/workspaces/${workspaceId}/reviews`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  listReviews: (workspaceId: string) => {
    return request<PlaceReview[]>(`/api/v1/workspaces/${workspaceId}/reviews`)
  }
}
