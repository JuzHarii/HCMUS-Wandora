import { useCallback, useEffect, useState } from 'react'
import { ArrowRight, CalendarDays, CalendarPlus, CircleAlert, LoaderCircle, Search, SlidersHorizontal, UsersRound } from 'lucide-react'
import { Link } from 'react-router'

import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { listWorkspaces, type Workspace } from '@/lib/api'
import { formatDashboardDates, formatRelativeDate, getSetupProgress } from '@/lib/trip-formatters'

export function TripDashboardPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('All')

  const loadWorkspaces = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      setWorkspaces(await listWorkspaces())
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Could not load your trips.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { void loadWorkspaces() }, [loadWorkspaces])

  const statusFilters = ['All', ...Array.from(new Set(workspaces.map((workspace) => workspace.status))).sort()]
  const normalizedQuery = query.trim().toLocaleLowerCase()
  const visibleWorkspaces = workspaces.filter((workspace) => {
    const matchesStatus = selectedStatus === 'All' || workspace.status === selectedStatus
    const searchable = `${workspace.title} ${workspace.destination} ${workspace.travel_style ?? ''}`.toLocaleLowerCase()
    return matchesStatus && (!normalizedQuery || searchable.includes(normalizedQuery))
  })
  const latestWorkspace = workspaces[0]

  return (
    <WorkspaceShell>
      <div data-testid="trip-dashboard" aria-labelledby="dashboard-title">
        <header className="dashboard-topbar"><div><p className="dashboard-kicker">Plan desk</p><h1 id="dashboard-title">My trips</h1><p>Open a saved plan or begin a new shared journey.</p></div><Link className="dashboard-create-button" to="/trips/new"><CalendarPlus aria-hidden="true" /> Create trip</Link></header>
        <div className="dashboard-controls" aria-label="Search and filter saved trips">
          <label className="dashboard-search"><Search aria-hidden="true" /><span className="sr-only">Search saved trips</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search saved trips" type="search" /></label>
          <div className="dashboard-filter-row"><SlidersHorizontal aria-hidden="true" /><div role="group" aria-label="Filter by trip status">{statusFilters.map((status) => <button className={selectedStatus === status ? 'is-selected' : ''} key={status} type="button" onClick={() => setSelectedStatus(status)}>{status}</button>)}</div></div>
        </div>
        {isLoading && <section className="dashboard-empty"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading your saved trips…</p></section>}
        {error && <section className="dashboard-empty"><CircleAlert aria-hidden="true" /><p>{error}</p><button className="dashboard-create-button" type="button" onClick={() => void loadWorkspaces()}>Try again</button></section>}
        {!isLoading && !error && workspaces.length === 0 && <section className="dashboard-empty"><CalendarPlus aria-hidden="true" /><h2>Your first trip starts here.</h2><p>Create a workspace and Wandora will draft the first itinerary for you.</p><Link className="dashboard-create-button" to="/trips/new">Create a trip <ArrowRight aria-hidden="true" /></Link></section>}
        {!isLoading && !error && workspaces.length > 0 && visibleWorkspaces.length === 0 && <section className="dashboard-empty dashboard-filter-empty"><Search aria-hidden="true" /><h2>No trips match that view.</h2><p>Try another search or show every saved trip.</p><button className="dashboard-create-button" type="button" onClick={() => { setQuery(''); setSelectedStatus('All') }}>Show all trips</button></section>}
        {!isLoading && !error && visibleWorkspaces.length > 0 && <div className="trip-dashboard-grid">
          {visibleWorkspaces.map((workspace, index) => <Link className="dashboard-trip-card" data-testid="dashboard-trip-card" key={workspace.id} to={`/trips/${workspace.id}`}>
            <div className={`dashboard-card-landscape dashboard-landscape-${index % 4}`}><span className="dashboard-card-orb" /><span className="dashboard-card-route" /><span className="dashboard-card-place">{workspace.destination}</span><span className="dashboard-card-status">{workspace.status}</span></div>
            <div className="dashboard-card-copy"><h2>{workspace.title}</h2><p><CalendarDays aria-hidden="true" /> {formatDashboardDates(workspace.start_date, workspace.end_date)}</p><p><UsersRound aria-hidden="true" /> {workspace.group_size ?? 1} traveler{workspace.group_size === 1 ? '' : 's'}</p></div>
            <div className="dashboard-card-footer"><div><span>{getSetupProgress(workspace)}% ready</span><i aria-hidden="true"><b style={{ width: `${getSetupProgress(workspace)}%` }} /></i></div><span className="dashboard-open-trip">Open <ArrowRight aria-hidden="true" /></span></div>
          </Link>)}
        </div>}
        {!isLoading && !error && workspaces.length > 0 && <section className="dashboard-recent" aria-label="Recent trip activity"><div><span className="dashboard-recent-dot" aria-hidden="true" /><div><strong>Recent activity</strong><p>{latestWorkspace ? `${latestWorkspace.title} was updated ${formatRelativeDate(latestWorkspace.updated_at)}.` : 'Your trip updates will appear here.'}</p></div></div><Link to={latestWorkspace ? `/trips/${latestWorkspace.id}` : '/trips/new'}>{latestWorkspace ? 'Review trip' : 'Create trip'} <ArrowRight aria-hidden="true" /></Link></section>}
      </div>
    </WorkspaceShell>
  )
}
