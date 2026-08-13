import type { Workspace } from '@/lib/api'

export function getSetupProgress(workspace: Workspace) {
  const completedFields = [
    workspace.destination,
    workspace.start_date && workspace.end_date,
    workspace.group_size,
    workspace.budget,
    workspace.travel_style,
    workspace.notes,
  ].filter(Boolean).length
  return Math.round((completedFields / 6) * 100)
}

export function formatDashboardDates(start: string | null, end: string | null) {
  if (!start || !end) return 'Dates to be confirmed'
  const startDate = new Date(`${start}T00:00:00`)
  const endDate = new Date(`${end}T00:00:00`)
  const sameMonth = startDate.getMonth() === endDate.getMonth() && startDate.getFullYear() === endDate.getFullYear()
  const month = new Intl.DateTimeFormat('en', { month: 'short' }).format(startDate)
  const year = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(endDate)
  return sameMonth ? `${month} ${startDate.getDate()}–${endDate.getDate()}, ${year}` : `${formatDay(start)} – ${formatDay(end)}`
}

export function formatRelativeDate(value: string) {
  const difference = Math.max(0, Date.now() - new Date(value).getTime())
  const days = Math.floor(difference / 86_400_000)
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  if (days < 7) return `${days} days ago`
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(new Date(value))
}

export function formatDay(value: string | null | undefined) {
  if (!value) return 'Flexible date'
  return new Intl.DateTimeFormat('en', { weekday: 'short', month: 'short', day: 'numeric' }).format(new Date(`${value}T00:00:00`))
}

export function formatDateRange(start: string | null | undefined, end: string | null | undefined) {
  if (!start || !end) return 'Dates to be confirmed'
  return `${formatDay(start)} – ${formatDay(end)}`
}

export function formatTime(value: string | null) {
  return value ? value.slice(0, 5) : 'Any time'
}
