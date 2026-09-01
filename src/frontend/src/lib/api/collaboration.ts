import { request } from './client'
import type { AuthUser } from './types'

export type WorkspaceMember = {
  id: string | number
  workspace_id: string | number
  user_id: string | number
  user_email?: string | null
  user_full_name?: string | null
  role: string
  joined_at: string
}

export const collaborationApi = {
  addMember: (workspaceId: string, payload: { email: string; role: string }) => {
    return request<WorkspaceMember>(`/api/v1/workspaces/${workspaceId}/members`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  listMembers: (workspaceId: string) => {
    return request<WorkspaceMember[]>(`/api/v1/workspaces/${workspaceId}/members`)
  },

  updateMemberRole: (workspaceId: string, userId: string, payload: { role: string }) => {
    return request<WorkspaceMember>(`/api/v1/workspaces/${workspaceId}/members/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
  },

  removeMember: (workspaceId: string, userId: string) => {
    return request<void>(`/api/v1/workspaces/${workspaceId}/members/${userId}`, {
      method: 'DELETE'
    })
  }
}
