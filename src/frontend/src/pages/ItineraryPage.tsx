import { useCallback, useEffect, useState } from 'react'
import { ArrowUpRight, CalendarPlus, CircleAlert, Compass, LayoutGrid, LoaderCircle } from 'lucide-react'
import { Link, useParams } from 'react-router'

import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { generateItinerary, getItinerary, getTripOverview, type Itinerary, type Workspace } from '@/lib/api'
import { formatDateRange, formatDay, formatTime } from '@/lib/trip-formatters'

export function ItineraryPage() {
  const { workspaceId = '' } = useParams()
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [itinerary, setItinerary] = useState<Itinerary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')

  const loadTrip = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const [overview, nextItinerary] = await Promise.all([getTripOverview(workspaceId), getItinerary(workspaceId)])
      setWorkspace(overview.workspace)
      setItinerary(nextItinerary)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Could not load this trip.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  async function regenerate() {
    setIsGenerating(true)
    setError('')
    try {
      setItinerary(await generateItinerary(workspaceId))
    } catch (generateError) {
      setError(generateError instanceof Error ? generateError.message : 'Could not regenerate the itinerary.')
    } finally {
      setIsGenerating(false)
    }
  }

  useEffect(() => { void loadTrip() }, [loadTrip])

  if (isLoading) return <WorkspaceShell><section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading your shared plan…</p></section></WorkspaceShell>
  if (error && !itinerary) return <WorkspaceShell><section className="workspace-loading"><CircleAlert aria-hidden="true" /><h1>We could not open this trip.</h1><p>{error}</p><button className="dashboard-create-button" type="button" onClick={() => void loadTrip()}>Try again</button></section></WorkspaceShell>

  return (
    <WorkspaceShell>
      <div className="workspace-view workspace-itinerary-view">
        <header className="workspace-view-header"><div><p className="dashboard-kicker">Shared itinerary</p><h1>{workspace?.title ?? 'Your trip plan'}</h1></div><div className="workspace-header-actions"><Link className="workspace-back-link" to="/home"><LayoutGrid aria-hidden="true" /> My trips</Link><Link className="dashboard-create-button" to="/trips/new"><CalendarPlus aria-hidden="true" /> New trip</Link></div></header>
        <section className="itinerary-hero"><div><p className="eyebrow"><Compass aria-hidden="true" /> Itinerary draft</p><p>{workspace?.destination} · {formatDateRange(workspace?.start_date, workspace?.end_date)} · {workspace?.group_size ?? 1} travelers</p></div><div className="itinerary-actions"><span className="status-pill">{workspace?.status ?? 'Draft'}</span><button data-testid="regenerate-itinerary-button" className="button button-primary" type="button" onClick={() => void regenerate()} disabled={isGenerating}>{isGenerating ? <><LoaderCircle className="spin" aria-hidden="true" /> Regenerating…</> : <><Compass aria-hidden="true" /> Regenerate itinerary</>}</button></div></section>
        {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" />{error}</div>}
        <section data-testid="itinerary-view" className="itinerary-timeline" aria-label="Generated itinerary">
          {itinerary?.days.map((day) => <article className="day-card" key={day.id}><header><div><span>Day {day.day_index}</span><h2>{day.title}</h2></div><time>{formatDay(day.travel_date)}</time></header>{day.summary && <p className="day-summary">{day.summary}</p>}<ol className="activity-list">{day.activities.map((activity) => <li key={activity.id} data-testid="activity-row" className="activity-row"><time>{formatTime(activity.start_time)}{activity.end_time ? ` – ${formatTime(activity.end_time)}` : ''}</time><div className="activity-marker" /><div><h3>{activity.title}</h3>{activity.location_name && <p>{activity.location_name}</p>}{activity.notes && <p className="activity-note">{activity.notes}</p>}{activity.external_url && <a href={activity.external_url} target="_blank" rel="noreferrer">Open map <ArrowUpRight aria-hidden="true" /></a>}</div></li>)}</ol></article>)}
        </section>
      </div>
    </WorkspaceShell>
  )
}
