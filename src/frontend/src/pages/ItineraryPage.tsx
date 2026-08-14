import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { ArrowUpRight, CalendarPlus, CircleAlert, Compass, History, LayoutGrid, LoaderCircle, Plus, RotateCcw, Trash2, Undo2 } from 'lucide-react'
import { Link, useParams } from 'react-router'

import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { addItineraryActivity, deleteItineraryActivity, generateItinerary, getItinerary, getTripOverview, initializeBlankItinerary, listItineraryVersions, restoreItineraryVersion, type Activity, type Itinerary, type ItineraryDay, type ItineraryVersion, type Workspace } from '@/lib/api'
import { formatDateRange, formatDay, formatTime } from '@/lib/trip-formatters'

export function ItineraryPage() {
  const { workspaceId = '' } = useParams()
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [itinerary, setItinerary] = useState<Itinerary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isInitializingBlank, setIsInitializingBlank] = useState(false)
  const [isRestoring, setIsRestoring] = useState(false)
  const [manualActivityCount, setManualActivityCount] = useState(0)
  const [versions, setVersions] = useState<ItineraryVersion[]>([])
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)
  const [error, setError] = useState('')

  const loadTrip = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const [overview, nextItinerary, nextVersions] = await Promise.all([getTripOverview(workspaceId), getItinerary(workspaceId), listItineraryVersions(workspaceId)])
      setWorkspace(overview.workspace)
      setManualActivityCount(overview.manual_activities)
      setItinerary(nextItinerary)
      setVersions(nextVersions)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Could not load this trip.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  async function regenerate() {
    if (manualActivityCount > 0 && !window.confirm(`Regenerate the AI suggestions? Your ${manualActivityCount} manual activit${manualActivityCount === 1 ? 'y' : 'ies'} will be kept.`)) return
    setIsGenerating(true)
    setError('')
    try {
      setItinerary(await generateItinerary(workspaceId))
      await loadTrip()
    } catch (generateError) {
      setError(generateError instanceof Error ? generateError.message : 'Could not regenerate the itinerary.')
    } finally {
      setIsGenerating(false)
    }
  }

  async function initializeBlank() {
    if (!window.confirm('Replace this itinerary with blank daily schedules? Existing activities will be removed.')) return
    setIsInitializingBlank(true)
    setError('')
    try {
      setItinerary(await initializeBlankItinerary(workspaceId))
      await loadTrip()
    } catch (blankError) {
      setError(blankError instanceof Error ? blankError.message : 'Could not initialize a blank itinerary.')
    } finally {
      setIsInitializingBlank(false)
    }
  }

  async function restoreVersion(version: ItineraryVersion) {
    if (!window.confirm('Restore this saved itinerary? The current itinerary will be replaced.')) return
    setIsRestoring(true)
    setError('')
    try {
      setItinerary(await restoreItineraryVersion(workspaceId, version.id))
      setIsHistoryOpen(false)
      await loadTrip()
    } catch (restoreError) {
      setError(restoreError instanceof Error ? restoreError.message : 'Could not restore this itinerary version.')
    } finally {
      setIsRestoring(false)
    }
  }

  useEffect(() => { void loadTrip() }, [loadTrip])

  if (isLoading) return <WorkspaceShell><section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading your shared plan…</p></section></WorkspaceShell>
  if (error && !itinerary) return <WorkspaceShell><section className="workspace-loading"><CircleAlert aria-hidden="true" /><h1>We could not open this trip.</h1><p>{error}</p><button className="dashboard-create-button" type="button" onClick={() => void loadTrip()}>Try again</button></section></WorkspaceShell>

  return (
    <WorkspaceShell>
      <div className="workspace-view workspace-itinerary-view">
        <header className="workspace-view-header"><div><p className="dashboard-kicker">Shared itinerary</p><h1>{workspace?.title ?? 'Your trip plan'}</h1></div><div className="workspace-header-actions"><Link className="workspace-back-link" to="/home"><LayoutGrid aria-hidden="true" /> My trips</Link><Link className="dashboard-create-button" to="/trips/new"><CalendarPlus aria-hidden="true" /> New trip</Link></div></header>
        <section className="itinerary-hero"><div><p className="eyebrow"><Compass aria-hidden="true" /> Itinerary draft</p><p>{workspace?.destination} · {formatDateRange(workspace?.start_date, workspace?.end_date)} · {workspace?.group_size ?? 1} travelers</p></div><div className="itinerary-actions"><span className={`generation-source generation-source-${itinerary?.generation_source ?? 'unknown'}`}>{formatGenerationSource(itinerary?.generation_source)}</span><span className="status-pill">{workspace?.status ?? 'Draft'}</span><div className="itinerary-action-buttons"><button className="button button-secondary itinerary-history-button" type="button" onClick={() => setIsHistoryOpen((open) => !open)} aria-expanded={isHistoryOpen}><History aria-hidden="true" /> History{versions.length > 0 ? ` (${versions.length})` : ''}</button><button data-testid="regenerate-itinerary-button" className="button button-primary" type="button" onClick={() => void regenerate()} disabled={isGenerating}>{isGenerating ? <><LoaderCircle className="spin" aria-hidden="true" /> Regenerating…</> : <><Compass aria-hidden="true" /> Regenerate itinerary</>}</button></div></div></section>
        {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span><button className="recovery-link" type="button" onClick={() => void initializeBlank()} disabled={isInitializingBlank}>{isInitializingBlank ? 'Preparing blank itinerary…' : 'Start with a blank itinerary'}</button></div>}
        {isHistoryOpen && <section className="itinerary-history" aria-label="Itinerary version history"><div><p className="dashboard-kicker">Version history</p><h2>Restore a previous draft</h2><p>Each AI regeneration saves the itinerary that came before it.</p></div>{versions.length === 0 ? <p className="history-empty">No previous versions yet. Regenerate once to create a restore point.</p> : <ol>{versions.map((version) => <li key={version.id}><div><strong>{formatGenerationSource(version.generation_source)}</strong><span>{formatVersionTime(version.created_at)}</span></div><button className="workspace-back-link" type="button" onClick={() => void restoreVersion(version)} disabled={isRestoring}>{isRestoring ? <LoaderCircle className="spin" aria-hidden="true" /> : <RotateCcw aria-hidden="true" />} Restore</button></li>)}</ol>}</section>}
        <section data-testid="itinerary-view" className="itinerary-timeline" aria-label="Generated itinerary">
          {itinerary?.days.map((day) => <DayCardEnhanced day={day} key={day.id} onActivityChanged={loadTrip} />)}
        </section>
      </div>
    </WorkspaceShell>
  )
}

function formatGenerationSource(source: string | null | undefined) {
  if (source === 'gemini') return 'Generated with Gemini'
  if (source === 'fallback') return 'Fallback itinerary'
  if (source === 'blank') return 'Blank itinerary'
  return 'Saved itinerary'
}

function formatVersionTime(value: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

function DayCardEnhanced({ day, onActivityChanged }: { day: ItineraryDay; onActivityChanged: () => Promise<void> }) {
  const [isAddingActivity, setIsAddingActivity] = useState(false)
  const [title, setTitle] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [locationName, setLocationName] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [pendingDeletion, setPendingDeletion] = useState<Activity | null>(null)
  const deleteTimer = useRef<number | null>(null)

  useEffect(() => () => {
    if (deleteTimer.current !== null) window.clearTimeout(deleteTimer.current)
  }, [])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!title.trim() || !startTime || !endTime) return setError('Add a name, start time, and end time.')
    if (endTime <= startTime) return setError('End time must be after start time.')
    setIsSubmitting(true)
    setError('')
    try {
      await addItineraryActivity({ day_id: day.id, title: title.trim(), start_time: startTime, end_time: endTime, location_name: locationName.trim() || undefined })
      await onActivityChanged()
      setTitle('')
      setStartTime('')
      setEndTime('')
      setLocationName('')
      setIsAddingActivity(false)
    } catch (activityError) {
      setError(activityError instanceof Error ? activityError.message : 'Could not add this activity.')
    } finally {
      setIsSubmitting(false)
    }
  }

  function scheduleDelete(activity: Activity) {
    if (deleteTimer.current !== null) window.clearTimeout(deleteTimer.current)
    setError('')
    setPendingDeletion(activity)
    deleteTimer.current = window.setTimeout(() => { void commitDelete(activity) }, 5000)
  }

  async function commitDelete(activity: Activity) {
    deleteTimer.current = null
    try {
      await deleteItineraryActivity(activity.id)
      await onActivityChanged()
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Could not remove this activity.')
    } finally {
      setPendingDeletion(null)
    }
  }

  function undoDelete() {
    if (deleteTimer.current !== null) window.clearTimeout(deleteTimer.current)
    deleteTimer.current = null
    setPendingDeletion(null)
  }

  const visibleActivities = day.activities.filter((activity) => activity.id !== pendingDeletion?.id)

  return <article className="day-card"><header><div><span>Day {day.day_index}</span><h2>{day.title}</h2></div><time>{formatDay(day.travel_date)}</time></header>{day.summary && <p className="day-summary">{day.summary}</p>}{visibleActivities.length > 0 ? <ol className="activity-list">{visibleActivities.map((activity) => <li key={activity.id} data-testid="activity-row" className="activity-row"><time>{formatTime(activity.start_time)}{activity.end_time ? ` - ${formatTime(activity.end_time)}` : ''}</time><div className="activity-marker" /><div><h3>{activity.title}</h3>{activity.location_name && <p>{activity.location_name}</p>}{activity.notes && <p className="activity-note">{activity.notes}</p>}{activity.external_url && <a href={activity.external_url} target="_blank" rel="noreferrer">Open map <ArrowUpRight aria-hidden="true" /></a>}</div><button className="activity-icon-button" type="button" aria-label={`Remove ${activity.title}`} title="Remove activity" onClick={() => scheduleDelete(activity)}><Trash2 aria-hidden="true" /></button></li>)}</ol> : <div className="blank-day"><p>No activities yet. Add the first stop for this day.</p></div>}{pendingDeletion && <div className="activity-undo" role="status"><span>{pendingDeletion.title} removed.</span><button type="button" onClick={undoDelete}><Undo2 aria-hidden="true" /> Undo</button></div>}{!isAddingActivity && <button className="draft-add-activity workspace-add-activity" type="button" onClick={() => setIsAddingActivity(true)}><Plus aria-hidden="true" /> Add activity</button>}{isAddingActivity && <form className="manual-activity-form" onSubmit={submit}><label>Activity<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Visit local market" autoFocus /></label><label>Start time<input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} /></label><label>End time<input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} /></label><label className="activity-location-field">Location<input value={locationName} onChange={(event) => setLocationName(event.target.value)} placeholder="Optional location" /></label>{error && <p className="form-error" role="alert">{error}</p>}<div><button className="dashboard-create-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Adding...' : 'Add activity'}</button><button className="recovery-link" type="button" onClick={() => { setIsAddingActivity(false); setError('') }} disabled={isSubmitting}>Cancel</button></div></form>}{error && !isAddingActivity && <p className="form-error" role="alert">{error}</p>}</article>
}

export function DayCard({ day, onActivityCreated }: { day: ItineraryDay; onActivityCreated: () => Promise<void> }) {
  const [isAddingActivity, setIsAddingActivity] = useState(false)
  const [title, setTitle] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [locationName, setLocationName] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!title.trim()) return setError('Enter an activity name.')
    setIsSubmitting(true)
    setError('')
    try {
      await addItineraryActivity({ day_id: day.id, title: title.trim(), start_time: startTime || undefined, end_time: endTime || undefined, location_name: locationName.trim() || undefined })
      await onActivityCreated()
      setTitle('')
      setStartTime('')
      setEndTime('')
      setLocationName('')
      setIsAddingActivity(false)
    } catch (activityError) {
      setError(activityError instanceof Error ? activityError.message : 'Could not add this activity.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return <article className="day-card"><header><div><span>Day {day.day_index}</span><h2>{day.title}</h2></div><time>{formatDay(day.travel_date)}</time></header>{day.summary && <p className="day-summary">{day.summary}</p>}{day.activities.length > 0 ? <ol className="activity-list">{day.activities.map((activity) => <li key={activity.id} data-testid="activity-row" className="activity-row"><time>{formatTime(activity.start_time)}{activity.end_time ? ` – ${formatTime(activity.end_time)}` : ''}</time><div className="activity-marker" /><div><h3>{activity.title}</h3>{activity.location_name && <p>{activity.location_name}</p>}{activity.notes && <p className="activity-note">{activity.notes}</p>}{activity.external_url && <a href={activity.external_url} target="_blank" rel="noreferrer">Open map <ArrowUpRight aria-hidden="true" /></a>}</div></li>)}</ol> : <div className={`blank-day ${isAddingActivity ? 'is-editing' : ''}`}><p>No activities yet. Add the first stop for this day.</p>{!isAddingActivity && <button className="recovery-link" type="button" onClick={() => setIsAddingActivity(true)}>Add activity</button>}{isAddingActivity && <form className="manual-activity-form" onSubmit={submit}><label>Activity<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Visit local market" autoFocus /></label><label>Start time<input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} /></label><label>End time<input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} /></label><label className="activity-location-field">Location<input value={locationName} onChange={(event) => setLocationName(event.target.value)} placeholder="Optional location" /></label>{error && <p className="form-error" role="alert">{error}</p>}<div><button className="dashboard-create-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Adding…' : 'Add activity'}</button><button className="recovery-link" type="button" onClick={() => setIsAddingActivity(false)} disabled={isSubmitting}>Cancel</button></div></form>}</div>}</article>
}
