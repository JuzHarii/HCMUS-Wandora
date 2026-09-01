import { request } from './client'
import type { AuthUser } from './types'

export type ChatMessage = {
  id: string
  workspace_id: string
  sender_id: string
  content: string
  created_at: string
  sender?: AuthUser
}

export type ChatHistory = {
  messages: ChatMessage[]
}

export const chatApi = {
  sendMessage: (workspaceId: string, payload: { content: string }) => {
    return request<ChatMessage>(`/api/v1/workspaces/${workspaceId}/chat`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  getHistory: (workspaceId: string) => {
    return request<ChatHistory>(`/api/v1/workspaces/${workspaceId}/messages`)
  }
}
