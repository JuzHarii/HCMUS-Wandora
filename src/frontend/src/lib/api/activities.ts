import { request } from './client'

export type ActivityComment = {
  id: string
  activity_id: string
  user_id: string
  user_name: string | null
  content: string
  created_at: string
}

export type ActivityVote = {
  id: string
  activity_id: string
  user_id: string
  vote_value: number
  created_at: string
}

export const activitiesApi = {
  listComments: (activityId: string) => {
    return request<ActivityComment[]>(`/api/v1/activities/${activityId}/comments`)
  },

  addComment: (activityId: string, content: string) => {
    return request<ActivityComment>(`/api/v1/activities/${activityId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    })
  },

  vote: (activityId: string, voteValue: number) => {
    return request<ActivityVote>(`/api/v1/activities/${activityId}/vote`, {
      method: 'POST',
      body: JSON.stringify({ vote_value: voteValue }),
    })
  }
}
