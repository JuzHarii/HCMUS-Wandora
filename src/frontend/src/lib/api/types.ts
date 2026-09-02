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
  current_user_role?: string | null
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

export type GeneratedActivity = {
  start_time: string | null
  end_time: string | null
  title: string
  location_name: string | null
  activity_type: string | null
  notes: string | null
  external_url: string | null
}

export type GeneratedItineraryDay = {
  day_index: number
  title: string
  summary: string | null
  travel_date: string | null
  activities: GeneratedActivity[]
}

export type ItineraryPreview = {
  source: string
  draft: { days: GeneratedItineraryDay[] }
}

export type TripOverview = {
  workspace: Workspace
  destinations: Array<{ destination_name: string; order_index: number }>
  itinerary_days: number
  itinerary_activities: number
  manual_activities: number
  current_user_role: string | null
  completed_planning_steps: number
  total_planning_steps: number
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
