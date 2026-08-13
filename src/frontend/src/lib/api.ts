import { getAccessToken } from '@/lib/auth-storage'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "")

export type AuthUser = {
  id: string
  email: string
  full_name: string
  role: string
  created_at: string
}

export type AuthSession = {
  access_token: string
  token_type: 'bearer'
  user: AuthUser
}

export type Workspace = {
  id: string
  title: string
  status: string
  itinerary_source: string | null
  itinerary_generated_at: string | null
  destination: string
  start_date: string | null
  end_date: string | null
  budget: number | null
  travel_style: string | null
  group_size: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export type Activity = {
  id: string
  day_id: string
  start_time: string | null
  end_time: string | null
  title: string
  location_name: string | null
  activity_type: string | null
  notes: string | null
  external_url: string | null
  is_manual: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export type ItineraryDay = {
  id: string
  workspace_id: string
  day_index: number
  travel_date: string | null
  title: string
  summary: string | null
  activities: Activity[]
}

export type Itinerary = {
  workspace_id: string
  generation_source: string | null
  generated_at: string | null
  days: ItineraryDay[]
}

export type ItineraryVersion = {
  id: string
  generation_source: string | null
  created_at: string
}

export type TripOverview = {
  workspace: Workspace
  destinations: Array<{ destination_name: string; order_index: number }>
  itinerary_days: number
  itinerary_activities: number
  manual_activities: number
}

export type CreateWorkspaceInput = {
  title: string
  destination: string
  start_date: string
  end_date: string
  budget?: number
  group_size?: number
  travel_style?: string
  notes?: string
}

type ApiErrorPayload = { detail?: string | Array<{ msg?: string }> }

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const accessToken = getAccessToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorPayload
    const detail = Array.isArray(body.detail)
      ? body.detail.map((item) => item.msg).filter(Boolean).join(" ")
      : body.detail
    throw new Error(detail || "Không thể hoàn tất yêu cầu. Vui lòng thử lại.")
  }
  return response.json() as Promise<T>
}

export function signUp(payload: { full_name: string; email: string; password: string }) {
  return request<AuthSession>('/api/v1/auth/signup', { method: 'POST', body: JSON.stringify(payload) })
}

export function login(payload: { email: string; password: string }) {
  return request<AuthSession>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) })
}

export function getCurrentUser() {
  return request<AuthUser>('/api/v1/auth/me')
}

export function createWorkspace(payload: CreateWorkspaceInput) {
  return request<Workspace>("/api/v1/workspaces", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function listWorkspaces() {
  return request<Workspace[]>('/api/v1/workspaces')
}

export function generateItinerary(workspaceId: string) {
  return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/generate-itinerary`, {
    method: "POST",
    body: JSON.stringify({ force_regenerate: true }),
  })
}

export type CreateActivityInput = {
  day_id: string
  title: string
  start_time?: string
  end_time?: string
  location_name?: string
  notes?: string
  activity_type?: string
  external_url?: string
}

export function initializeBlankItinerary(workspaceId: string) {
  return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/initialize-blank-itinerary`, {
    method: 'POST',
  })
}

export function addItineraryActivity(payload: CreateActivityInput) {
  return request<Activity>('/api/v1/itineraries/activities', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getTripOverview(workspaceId: string) {
  return request<TripOverview>(`/api/v1/workspaces/${workspaceId}/overview`)
}

export function getItinerary(workspaceId: string) {
  return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/itinerary`)
}

export function listItineraryVersions(workspaceId: string) {
  return request<ItineraryVersion[]>(`/api/v1/workspaces/${workspaceId}/itinerary-versions`)
}

export function restoreItineraryVersion(workspaceId: string, versionId: string) {
  return request<Itinerary>(`/api/v1/workspaces/${workspaceId}/itinerary-versions/${versionId}/restore`, {
    method: 'POST',
  })
}
