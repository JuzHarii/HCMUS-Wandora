import { useCallback, useEffect, useState } from 'react'
import { Link, Outlet, useLocation, useParams } from 'react-router'
import { CircleAlert, LoaderCircle, Map, Briefcase, Users, Star, Share2 } from 'lucide-react'

import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { workspacesApi, type Workspace } from '@/lib/api'

export function TripWorkspacePage() {
  const { workspaceId = '' } = useParams()
  const { pathname } = useLocation()
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const loadTrip = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const overview = await workspacesApi.getTripOverview(workspaceId)
      setWorkspace(overview.workspace)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load this trip.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  useEffect(() => { void loadTrip() }, [loadTrip])

  if (isLoading) return <WorkspaceShell><section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading your trip…</p></section></WorkspaceShell>
  if (error || !workspace) return <WorkspaceShell><section className="workspace-loading"><CircleAlert aria-hidden="true" /><h1>We could not open this trip.</h1><p>{error}</p><button className="dashboard-create-button" type="button" onClick={() => void loadTrip()}>Try again</button></section></WorkspaceShell>

  const isDraft = workspace.status === 'Draft'

  return (
    <WorkspaceShell>
      <div className="trip-workspace">
        <header className="workspace-view-header workspace-tabs-header">
          <div>
            <p className="dashboard-kicker">Shared workspace</p>
            <h1>{workspace.title}</h1>
          </div>
          <nav className="workspace-tabs">
            <Link to="itinerary" className={`workspace-tab ${pathname.includes('/itinerary') ? 'is-active' : ''}`}><Map aria-hidden="true" /> Itinerary</Link>
            <Link to="packing" className={`workspace-tab ${pathname.includes('/packing') ? 'is-active' : ''}`} style={isDraft ? { pointerEvents: 'none', opacity: 0.5 } : {}}><Briefcase aria-hidden="true" /> Packing</Link>
            <Link to="members" className={`workspace-tab ${pathname.includes('/members') ? 'is-active' : ''}`} style={isDraft ? { pointerEvents: 'none', opacity: 0.5 } : {}}><Users aria-hidden="true" /> Members</Link>
            <Link to="reviews" className={`workspace-tab ${pathname.includes('/reviews') ? 'is-active' : ''}`} style={isDraft ? { pointerEvents: 'none', opacity: 0.5 } : {}}><Star aria-hidden="true" /> Reviews</Link>
            <Link to="share" className={`workspace-tab ${pathname.includes('/share') ? 'is-active' : ''}`} style={isDraft ? { pointerEvents: 'none', opacity: 0.5 } : {}}><Share2 aria-hidden="true" /> Share & Export</Link>
          </nav>
        </header>
        <div className="workspace-tab-content">
          <Outlet context={{ workspace }} />
        </div>
      </div>
    </WorkspaceShell>
  )
}
