import { request } from './client'

export type PackingListEntry = {
  id: string | number
  packing_item_id: string | number
  user_id: string | number
  user_email?: string | null
  user_full_name?: string | null
  is_checked: boolean
}

export type PackingItem = {
  id: string
  workspace_id: string
  name: string
  category?: string | null
  assignments: PackingListEntry[]
  created_at: string
}

export const packingApi = {
  generateSuggestions: (workspaceId: string) => {
    return request<PackingItem[]>(`/api/v1/workspaces/${workspaceId}/packing/suggestions`, {
      method: 'POST'
    })
  },

  listItems: (workspaceId: string) => {
    return request<PackingItem[]>(`/api/v1/workspaces/${workspaceId}/packing`)
  },

  addItem: (workspaceId: string, payload: { name: string; category?: string; assigned_to?: string }) => {
    return request<PackingItem>(`/api/v1/workspaces/${workspaceId}/packing/items`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  updateItem: (itemId: string, payload: { name?: string; category?: string; is_checked?: boolean }) => {
    return request<PackingItem>(`/api/v1/packing/items/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
  },

  assignItem: (itemId: string, payload: { user_id: string | number; is_checked?: boolean }) => {
    return request<PackingItem>(`/api/v1/packing/items/${itemId}/assign`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  deleteItem: (itemId: string) => {
    return request<void>(`/api/v1/packing/items/${itemId}`, {
      method: 'DELETE'
    })
  }
}
