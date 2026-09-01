import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useOutletContext, useParams } from 'react-router'
import { ArrowUpRight, CircleAlert, Compass, History, LoaderCircle, RotateCcw, Sparkles, MessageCircle, Send, X } from 'lucide-react'

import { workspacesApi, itinerariesApi, activitiesApi, type ActivityComment, type Itinerary, type ItineraryDay, type ItineraryVersion, type Workspace, type Activity, type ItineraryPreview } from '@/lib/api'
import { formatDateRange, formatDay, formatTime } from '@/lib/trip-formatters'

export function ItineraryTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>()
  const { workspaceId = '' } = useParams()
  const [itinerary, setItinerary] = useState<Itinerary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isInitializingBlank, setIsInitializingBlank] = useState(false)
  const [restoringVersionId, setRestoringVersionId] = useState<string | number | null>(null)
  const [manualActivityCount, setManualActivityCount] = useState(0)
  const [versions, setVersions] = useState<ItineraryVersion[]>([])
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)
  const [error, setError] = useState('')
  const [adjustPrompt, setAdjustPrompt] = useState('')
  const [isAdjusting, setIsAdjusting] = useState(false)
  const [previewDraft, setPreviewDraft] = useState<ItineraryPreview | null>(null)
  const canEdit = workspace.current_user_role !== 'viewer'

  const loadTrip = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const [nextItinerary, nextVersions] = await Promise.all([workspacesApi.getItinerary(workspaceId), workspacesApi.listItineraryVersions(workspaceId)])
      setManualActivityCount(workspace.manual_activities)
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
      setItinerary(await workspacesApi.generateItinerary(workspaceId))
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
      setItinerary(await workspacesApi.initializeBlankItinerary(workspaceId))
      await loadTrip()
    } catch (blankError) {
      setError(blankError instanceof Error ? blankError.message : 'Could not initialize a blank itinerary.')
    } finally {
      setIsInitializingBlank(false)
    }
  }

  async function submitAdjustment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!adjustPrompt.trim()) return
    setIsAdjusting(true)
    setError('')
    try {
      const preview = await workspacesApi.previewAdjustment(workspaceId, { prompt: adjustPrompt.trim() })
      setPreviewDraft(preview)
      setAdjustPrompt('')
    } catch (e: any) {
      setError('AI could not process that request. Please rephrase or try again.')
    } finally {
      setIsAdjusting(false)
    }
  }

  async function applyAdjustment() {
    if (!previewDraft) return
    setIsAdjusting(true)
    setError('')
    try {
      setItinerary(await workspacesApi.applyAdjustment(workspaceId, previewDraft))
      setPreviewDraft(null)
      await loadTrip()
    } catch (e: any) {
      setError(e.message || 'Could not apply adjustment.')
    } finally {
      setIsAdjusting(false)
    }
  }

  async function restoreVersion(version: ItineraryVersion) {
    if (!window.confirm('Restore this saved itinerary? The current itinerary will be replaced.')) return
    setRestoringVersionId(version.id)
    setError('')
    try {
      setItinerary(await workspacesApi.restoreItineraryVersion(workspaceId, String(version.id)))
      setIsHistoryOpen(false)
      await loadTrip()
    } catch (restoreError) {
      setError(restoreError instanceof Error ? restoreError.message : 'Could not restore this itinerary version.')
    } finally {
      setRestoringVersionId(null)
    }
  }

  useEffect(() => { void loadTrip() }, [loadTrip])

  if (isLoading) return <section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading itinerary…</p></section>
  if (error && !itinerary) return <section className="workspace-loading"><CircleAlert aria-hidden="true" /><h1>We could not open this itinerary.</h1><p>{error}</p><button className="dashboard-create-button" type="button" onClick={() => void loadTrip()}>Try again</button></section>

  const mappedPreviewItinerary = previewDraft ? {
    workspace_id: workspace.id,
    generation_source: previewDraft.source,
    generated_at: new Date().toISOString(),
    days: previewDraft.draft.days.map((d: any) => ({
      id: `preview-${d.day_index}`,
      workspace_id: workspace.id,
      day_index: d.day_index,
      date_value: d.travel_date,
      travel_date: d.travel_date,
      title: d.title,
      summary: d.summary,
      activities: d.activities.map((a: any, i: number) => ({
        id: `preview-act-${d.day_index}-${i}`,
        day_id: `preview-${d.day_index}`,
        title: a.title,
        start_time: a.start_time,
        end_time: a.end_time,
        location_name: a.location_name,
        activity_type: a.activity_type,
        notes: a.notes,
        external_url: a.external_url,
        is_manual: false,
        order_index: i,
        sort_order: i,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }))
    }))
  } as Itinerary : null;

  return (
    <div className="workspace-view workspace-itinerary-view">
      <section className="itinerary-hero"><div><p className="eyebrow"><Compass aria-hidden="true" /> Itinerary draft</p><p>{workspace.destination} · {formatDateRange(workspace.start_date, workspace.end_date)} · {workspace.group_size ?? 1} travelers</p></div><div className="itinerary-actions"><span className={`generation-source generation-source-${itinerary?.generation_source ?? 'unknown'}`}>{formatGenerationSource(itinerary?.generation_source)}</span><span className="status-pill">{workspace.status ?? 'Draft'}</span><div className="itinerary-action-buttons"><button className="button button-secondary itinerary-history-button" type="button" onClick={() => setIsHistoryOpen((open) => !open)} aria-expanded={isHistoryOpen}><History aria-hidden="true" /> History{versions.length > 0 ? ` (${versions.length})` : ''}</button>{canEdit && <button data-testid="regenerate-itinerary-button" className="button button-primary" type="button" onClick={() => void regenerate()} disabled={isGenerating}>{isGenerating ? <><LoaderCircle className="spin" aria-hidden="true" /> Regenerating…</> : <><Compass aria-hidden="true" /> Regenerate itinerary</>}</button>}</div></div></section>
      {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span>{canEdit && <button className="recovery-link" type="button" onClick={() => void initializeBlank()} disabled={isInitializingBlank}>{isInitializingBlank ? 'Preparing blank itinerary…' : 'Start with a blank itinerary'}</button>}</div>}
      
      {canEdit && <section className="itinerary-ai-adjust" style={{ padding: '1rem', background: 'var(--color-surface-dim)', borderRadius: '0.75rem', marginBottom: '1.5rem' }}>
        <form onSubmit={submitAdjustment} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <input 
            value={adjustPrompt} 
            onChange={(e) => setAdjustPrompt(e.target.value)} 
            placeholder="e.g. Change the museum on Day 2 to an outdoor activity..." 
            disabled={isAdjusting}
            style={{ flex: 1, padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid var(--color-border)' }}
          />
          <button className="button button-primary" type="submit" disabled={isAdjusting || !adjustPrompt.trim()}>
            {isAdjusting ? <><LoaderCircle className="spin" aria-hidden="true" /> Adjusting…</> : <><Sparkles aria-hidden="true" /> Adjust with AI</>}
          </button>
        </form>
      </section>}

      {isHistoryOpen && <section className="itinerary-history" aria-label="Itinerary version history"><div><p className="dashboard-kicker">Version history</p><h2>Restore a previous draft</h2><p>Each AI regeneration saves the itinerary that came before it.</p></div>{versions.length === 0 ? <p className="history-empty">No previous versions yet. Regenerate once to create a restore point.</p> : <ol>{versions.map((version) => <li key={version.id}><div><strong>{formatGenerationSource(version.generation_source)}</strong><span>{formatVersionTime(version.created_at)}</span></div>{canEdit && <button className="workspace-back-link" type="button" onClick={() => void restoreVersion(version)} disabled={restoringVersionId !== null}>{restoringVersionId === version.id ? <LoaderCircle className="spin" aria-hidden="true" /> : <RotateCcw aria-hidden="true" />} Restore</button>}</li>)}</ol>}</section>}
      <section data-testid="itinerary-view" className="itinerary-timeline" aria-label="Generated itinerary">
        {previewDraft && mappedPreviewItinerary ? (
          <div className="preview-overlay" style={{ border: '2px dashed var(--color-brand)', padding: '1rem', borderRadius: '0.75rem', background: 'var(--color-surface-dim)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h2 style={{ margin: 0, color: 'var(--color-brand)' }}>Preview AI Adjustment</h2>
                <p style={{ margin: '0.25rem 0 0 0', color: 'var(--color-text-dim)', fontSize: '0.9rem' }}>Review the proposed changes. You can accept this draft or discard it to keep your current itinerary.</p>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button className="button button-secondary" type="button" onClick={() => setPreviewDraft(null)} disabled={isAdjusting}>Discard</button>
                <button className="button button-primary" type="button" onClick={() => void applyAdjustment()} disabled={isAdjusting}>
                  {isAdjusting ? <LoaderCircle className="spin" aria-hidden="true" /> : 'Accept Proposal'}
                </button>
              </div>
            </div>
            {mappedPreviewItinerary.days.map((day) => <DayCard day={day} key={day.id} onActivityCreated={async () => {}} canEdit={false} />)}
          </div>
        ) : (
          itinerary?.days.map((day) => <DayCard day={day} key={day.id} onActivityCreated={loadTrip} canEdit={canEdit} />)
        )}
      </section>
    </div>
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

function DayCard({ day, onActivityCreated, canEdit }: { day: ItineraryDay; onActivityCreated: () => Promise<void>; canEdit: boolean }) {
  const [isAddingActivity, setIsAddingActivity] = useState(false)
  const [title, setTitle] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [locationName, setLocationName] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [notes, setNotes] = useState('')
  const [externalUrl, setExternalUrl] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!title.trim()) return setError('Enter an activity name.')
    setIsSubmitting(true)
    setError('')
    try {
      await itinerariesApi.addActivity({ day_id: day.id, title: title.trim(), start_time: startTime || undefined, end_time: endTime || undefined, location_name: locationName.trim() || undefined, notes: notes.trim() || undefined, external_url: externalUrl.trim() || undefined })
      await onActivityCreated()
      setTitle('')
      setStartTime('')
      setEndTime('')
      setLocationName('')
      setNotes('')
      setExternalUrl('')
      setIsAddingActivity(false)
    } catch (activityError) {
      setError(activityError instanceof Error ? activityError.message : 'Could not add this activity.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return <article className="day-card"><header><div><span>Day {day.day_index}</span><h2>{day.title}</h2></div><time>{formatDay(day.travel_date)}</time></header>{day.summary && <p className="day-summary">{day.summary}</p>}{day.activities.length > 0 ? <ol className="activity-list">{day.activities.map((activity) => <ActivityRow key={activity.id} activity={activity} canEdit={canEdit} onActivityUpdated={onActivityCreated} />)}</ol> : <p style={{ color: 'var(--color-text-dim)', fontSize: '0.9rem', marginBottom: '1rem' }}>No activities yet.</p>}{canEdit && <div className={`blank-day ${isAddingActivity ? 'is-editing' : ''}`}>{!isAddingActivity && <button className="recovery-link" type="button" onClick={() => setIsAddingActivity(true)}>+ Add activity</button>}{isAddingActivity && <form className="manual-activity-form" onSubmit={submit}><label>Activity<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Visit local market" autoFocus /></label><label>Start time<input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} /></label><label>End time<input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} /></label><label className="activity-location-field">Location<input value={locationName} onChange={(event) => setLocationName(event.target.value)} placeholder="Optional location" /></label><label>Notes<textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Optional tips, reminders..." rows={2} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)', resize: 'vertical' }} /></label><label>External Link<input type="url" value={externalUrl} onChange={(event) => setExternalUrl(event.target.value)} placeholder="https://..." style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)' }} /></label>{error && <p className="form-error" role="alert">{error}</p>}<div><button className="dashboard-create-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Adding…' : 'Save'}</button><button className="recovery-link" type="button" onClick={() => setIsAddingActivity(false)} disabled={isSubmitting}>Cancel</button></div></form>}</div>}</article>
}

function ActivityRow({ activity, canEdit, onActivityUpdated }: { activity: Activity; canEdit: boolean; onActivityUpdated: () => Promise<void> }) {
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState(activity.title || '')
  const [startTime, setStartTime] = useState(activity.start_time ? activity.start_time.substring(0, 5) : '')
  const [endTime, setEndTime] = useState(activity.end_time ? activity.end_time.substring(0, 5) : '')
  const [locationName, setLocationName] = useState(activity.location_name || '')
  const [notes, setNotes] = useState(activity.notes || '')
  const [externalUrl, setExternalUrl] = useState(activity.external_url || '')
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!title.trim()) return setError('Enter an activity name.')
    setIsSubmitting(true)
    setError('')
    try {
      await itinerariesApi.updateActivity(activity.id, {
        title: title.trim(),
        start_time: startTime || null,
        end_time: endTime || null,
        location_name: locationName.trim() || null,
        notes: notes.trim() || null,
        external_url: externalUrl.trim() || null,
      })
      await onActivityUpdated()
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update this activity.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isEditing) {
    return (
      <li className="activity-row is-editing-row">
        <form className="manual-activity-form" onSubmit={submit} style={{ width: '100%' }}>
          <label>Activity<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Visit local market" autoFocus /></label>
          <label>Start time<input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} /></label>
          <label>End time<input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} /></label>
          <label className="activity-location-field">Location<input value={locationName} onChange={(event) => setLocationName(event.target.value)} placeholder="Optional location" /></label>
          <label>Notes<textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Optional tips, reminders..." rows={2} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)', resize: 'vertical' }} /></label>
          <label>External Link<input type="url" value={externalUrl} onChange={(event) => setExternalUrl(event.target.value)} placeholder="https://..." style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)' }} /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <div style={{ marginTop: '0.5rem' }}>
            <button className="dashboard-create-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Saving…' : 'Save'}</button>
            <button className="recovery-link" type="button" onClick={() => setIsEditing(false)} disabled={isSubmitting}>Cancel</button>
          </div>
        </form>
      </li>
    )
  }

  return (
    <li data-testid="activity-row" className="activity-row">
      <time>{formatTime(activity.start_time)}{activity.end_time ? ` – ${formatTime(activity.end_time)}` : ''}</time>
      <div className="activity-marker" />
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <h3>{activity.title}</h3>
          {canEdit && (
            <button type="button" onClick={() => setIsEditing(true)} className="recovery-link" style={{ fontSize: '0.85rem', padding: '0.25rem 0.5rem' }}>
              Edit Notes
            </button>
          )}
        </div>
        {activity.location_name && <p>{activity.location_name}</p>}
        {activity.notes && <p className="activity-note">{activity.notes}</p>}
        {activity.external_url && <a href={activity.external_url} target="_blank" rel="noreferrer">Open map <ArrowUpRight aria-hidden="true" /></a>}
        <ActivityComments activity={activity} />
      </div>
    </li>
  )
}

function ActivityComments({ activity }: { activity: Activity }) {
  const [isOpen, setIsOpen] = useState(false)
  const [comments, setComments] = useState<ActivityComment[]>([])
  const [content, setContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const loadComments = useCallback(async () => {
    try {
      setComments(await activitiesApi.listComments(activity.id))
    } catch (e) {
      // Ignore
    }
  }, [activity.id])

  useEffect(() => {
    if (isOpen) void loadComments()
  }, [isOpen, loadComments])

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (!content.trim()) return
    setIsLoading(true)
    try {
      await activitiesApi.addComment(activity.id, content.trim())
      setContent('')
      await loadComments()
    } catch (e) {
      // Ignore
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) {
    return (
      <button 
        type="button" 
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-1.5 mt-3 text-[0.8rem] font-bold text-[var(--color-brand)] hover:text-[var(--color-brand-hover)] transition-colors cursor-pointer"
      >
        <MessageCircle size={14} />
        <span>Discuss</span>
      </button>
    )
  }

  return (
    <div className="mt-4 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded-2xl overflow-hidden shadow-sm transition-all">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border-subtle)] bg-[var(--color-sage)]/30">
        <strong className="text-[0.7rem] font-bold text-[var(--color-ink)] uppercase tracking-wider flex items-center gap-1.5">
          <MessageCircle size={14} className="text-[var(--color-moss)]" />
          Discussion
        </strong>
        <button 
          type="button" 
          onClick={() => setIsOpen(false)}
          className="text-[var(--color-ink-muted)] hover:text-[var(--color-brand)] transition-colors rounded-full p-1 hover:bg-[var(--color-sage)] cursor-pointer"
        >
          <X size={16} />
        </button>
      </div>
      
      <div className="max-h-[240px] overflow-y-auto p-4 flex flex-col gap-4">
        {comments.length === 0 ? (
          <p className="text-[0.85rem] text-[var(--color-ink-muted)] text-center py-6 italic">No comments yet. Start the conversation!</p>
        ) : (
          comments.map(c => (
            <div key={c.id} className="flex flex-col gap-1">
              <span className="text-[0.65rem] font-bold uppercase tracking-wide text-[var(--color-moss)] ml-1">{c.user_name || 'Member'}</span>
              <div className="bg-[var(--color-sage)]/60 px-3 py-2.5 rounded-2xl rounded-tl-sm text-[0.85rem] text-[var(--color-ink)] w-fit max-w-[90%] leading-relaxed shadow-sm">
                {c.content}
              </div>
            </div>
          ))
        )}
      </div>
      
      <form onSubmit={submit} className="flex gap-2 p-3 border-t border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
        <input 
          value={content} 
          onChange={e => setContent(e.target.value)} 
          placeholder="Type a message..." 
          className="flex-1 px-4 py-2 rounded-full border border-[var(--color-border-subtle)] text-[0.85rem] text-[var(--color-ink)] focus:outline-none focus:border-[var(--color-brand)] focus:ring-1 focus:ring-[var(--color-brand)] bg-white transition-all"
        />
        <button 
          type="submit" 
          disabled={isLoading || !content.trim()} 
          className="flex items-center justify-center w-9 h-9 rounded-full bg-[var(--color-brand)] text-white hover:bg-[var(--color-brand-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
        >
          {isLoading ? <LoaderCircle size={16} className="spin" /> : <Send size={14} className="ml-0.5" />}
        </button>
      </form>
    </div>
  )
}
