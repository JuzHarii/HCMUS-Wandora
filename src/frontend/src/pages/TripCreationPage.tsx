import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { ArrowLeft, ArrowRight, Check, ChevronLeft, CircleAlert, Compass, LoaderCircle, MapPinned, PencilLine, Plus, Sparkles, Trash2, Undo2, UsersRound } from 'lucide-react'
import { Link, useNavigate } from 'react-router'

import { FormField } from '@/components/forms/FormField'
import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { workspacesApi, tripsApi, type CreateWorkspaceInput, type GeneratedItineraryDay, type ItineraryPreview, type Workspace } from '@/lib/api'
import { formatDay } from '@/lib/trip-formatters'

type Step = 'invitation' | 'details' | 'review'
type DraftUndo = { dayIndex: number; activityIndex: number; activity: GeneratedActivity }

type TripFormValues = {
  destination: string
  start_date: string
  end_date: string
  group_size: string
  budget: string
  pace: string
  interests: string[]
  mustSee: string[]
  avoid: string
  notes: string
}

const STEPS: Array<{ key: Step; label: string; caption: string }> = [
  { key: 'invitation', label: 'Invitation', caption: 'Invite your group' },
  { key: 'details', label: 'Details', caption: 'Places and preferences' },
  { key: 'review', label: 'Review', caption: 'Draft and save' },
]

const INTERESTS = ['Food markets', 'Heritage sites', 'Photo spots', 'Beach time', 'Nature walks', 'Nightlife']
const PACES = ['Slow mornings', 'Balanced days', 'Packed schedule']

export function TripCreationPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState<Step>('invitation')
  const [form, setForm] = useState<TripFormValues>({ destination: '', start_date: '', end_date: '', group_size: '2', budget: '', pace: 'Balanced days', interests: ['Food markets'], mustSee: ['', '', ''], avoid: '', notes: '' })
  const [errors, setErrors] = useState<Partial<Record<'destination' | 'start_date' | 'end_date' | 'group_size' | 'budget', string>>>({})
  const [preview, setPreview] = useState<ItineraryPreview | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [apiError, setApiError] = useState('')
  const [duplicateWarning, setDuplicateWarning] = useState<string | null>(null)
  const [isCheckingDuplicates, setIsCheckingDuplicates] = useState(false)
  const [savedWorkspace, setSavedWorkspace] = useState<Workspace | null>(null)
  const [draftUndo, setDraftUndo] = useState<DraftUndo | null>(null)
  const draftUndoTimer = useRef<number | null>(null)

  const stepIndex = STEPS.findIndex((item) => item.key === step)
  const estimatedTravelers = Number(form.group_size || 1)
  const tripInput = useMemo(() => buildTripInput(form, estimatedTravelers), [form, estimatedTravelers])

  useEffect(() => () => {
    if (draftUndoTimer.current !== null) window.clearTimeout(draftUndoTimer.current)
  }, [])

  function updateField<K extends keyof TripFormValues>(field: K, value: TripFormValues[K]) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  function validateDetails() {
    const nextErrors: typeof errors = {}
    if (!form.destination.trim()) nextErrors.destination = 'Choose a destination for this trip.'
    if (!form.start_date) nextErrors.start_date = 'Choose a start date.'
    if (!form.end_date) nextErrors.end_date = 'Choose an end date.'
    if (form.start_date && form.end_date && form.end_date < form.start_date) nextErrors.end_date = 'End date must be after or equal to start date.'
    const groupSizeNum = Number(form.group_size)
    if (!Number.isInteger(groupSizeNum) || groupSizeNum < 1 || groupSizeNum > 10000) {
      nextErrors.group_size = 'Group size must be a valid number between 1 and 10,000.'
    }
    if (form.budget && (!Number.isInteger(Number(form.budget)) || Number(form.budget) < 0)) nextErrors.budget = 'Budget must be a whole number of 0 or more.'
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  async function nextStep() {
    if (step === 'invitation') return setStep('details')
    if (step === 'details' && validateDetails()) {
      if (!duplicateWarning) {
        setIsCheckingDuplicates(true)
        try {
          const res = await tripsApi.checkDuplicates(tripInput)
          if (res.has_duplicate) {
            setDuplicateWarning('Warning: You have a trip with similar destination or dates. Are you sure you want to create a new one?')
            return
          }
        } catch (e) {
          // Ignore if API fails
        } finally {
          setIsCheckingDuplicates(false)
        }
      }
      setDuplicateWarning(null)
      setStep('review')
    }
  }

  async function generatePreview() {
    setIsGenerating(true)
    setApiError('')
    try {
      setPreview(await workspacesApi.previewItinerary(tripInput))
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Could not generate the itinerary draft.')
    } finally {
      setIsGenerating(false)
    }
  }

  function generateBlankItinerary() {
    setIsGenerating(false)
    setApiError('')
    const days = Array.from({ length: tripDayCount(tripInput.start_date, tripInput.end_date) }).map((_, i) => {
      const travelDate = new Date(new Date(tripInput.start_date).getTime() + i * 86400000)
      return {
        day_index: i + 1,
        travel_date: travelDate.toISOString().split('T')[0],
        title: `Day ${i + 1}`,
        summary: '',
        activities: []
      }
    })
    setPreview({
      source: 'fallback',
      draft: { days }
    })
  }

  function updateDraftDay(dayIndex: number, field: 'title' | 'summary', value: string) {
    setPreview((current) => current ? { ...current, draft: { days: current.draft.days.map((day) => day.day_index === dayIndex ? { ...day, [field]: value } : day) } } : current)
  }

  function updateDraftActivity(dayIndex: number, activityIndex: number, field: 'title' | 'start_time' | 'end_time' | 'location_name', value: string) {
    setPreview((current) => current ? { ...current, draft: { days: current.draft.days.map((day) => day.day_index === dayIndex ? { ...day, activities: day.activities.map((activity, index) => index === activityIndex ? { ...activity, [field]: value || null } : activity) } : day) } } : current)
  }

  function addDraftActivity(dayIndex: number, activity: GeneratedActivity) {
    setPreview((current) => current ? { ...current, draft: { days: current.draft.days.map((day) => day.day_index === dayIndex ? { ...day, activities: [...day.activities, activity] } : day) } } : current)
  }

  function removeDraftActivity(dayIndex: number, activityIndex: number) {
    const activity = preview?.draft.days.find((day) => day.day_index === dayIndex)?.activities[activityIndex]
    if (!activity) return
    if (draftUndoTimer.current !== null) window.clearTimeout(draftUndoTimer.current)
    setPreview((current) => current ? { ...current, draft: { days: current.draft.days.map((day) => day.day_index === dayIndex ? { ...day, activities: day.activities.filter((_, index) => index !== activityIndex) } : day) } } : current)
    setDraftUndo({ dayIndex, activityIndex, activity })
    draftUndoTimer.current = window.setTimeout(() => setDraftUndo(null), 5000)
  }

  function undoDraftRemoval() {
    if (!draftUndo) return
    if (draftUndoTimer.current !== null) window.clearTimeout(draftUndoTimer.current)
    const { dayIndex, activityIndex, activity } = draftUndo
    setPreview((current) => current ? { ...current, draft: { days: current.draft.days.map((day) => {
      if (day.day_index !== dayIndex) return day
      const activities = [...day.activities]
      activities.splice(activityIndex, 0, activity)
      return { ...day, activities }
    }) } } : current)
    setDraftUndo(null)
  }

  async function saveTrip() {
    if (!preview) return
    if (!hasValidDraftActivities(preview)) {
      setApiError('Each added activity needs a name, start time, and end time before you save the trip.')
      return
    }
    setIsSaving(true)
    setApiError('')
    try {
      const workspace = await workspacesApi.createWorkspace(tripInput)
      await workspacesApi.saveItineraryDraft(workspace.id, preview)
      setSavedWorkspace(workspace)
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Could not save this trip.')
    } finally {
      setIsSaving(false)
    }
  }

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (step === 'review' && preview && !isSaving && !savedWorkspace) {
        e.preventDefault()
        e.returnValue = '' // Required for Chrome to show the prompt
      }
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [step, preview, isSaving, savedWorkspace])

  const handleLeave = (e: React.MouseEvent) => {
    if (step === 'review' && preview && !savedWorkspace) {
      if (!window.confirm('Your preview will not be saved as a trip. Are you sure you want to leave?')) {
        e.preventDefault()
      }
    }
  }

  if (savedWorkspace) {
    return <WorkspaceShell><div className="workspace-view wizard-complete-view"><section className="wizard-complete-card"><span className="wizard-complete-mark"><Check aria-hidden="true" /></span><p className="dashboard-kicker">Trip saved</p><h1>Your shared plan is ready.</h1><p>{savedWorkspace.title} now has its first itinerary draft. You can invite teammates from the trip workspace later.</p><button data-testid="open-trip-workspace" className="flow-submit" type="button" onClick={() => navigate(`/trips/${savedWorkspace.id}`)}>Open trip workspace <ArrowRight aria-hidden="true" /></button></section></div></WorkspaceShell>
  }

  return (
    <WorkspaceShell>
      <div className="workspace-view wizard-view">
        <header className="workspace-view-header"><div><p className="dashboard-kicker">New shared plan</p><h1>Shape the trip together.</h1></div><Link className="workspace-back-link" to="/home" onClick={handleLeave}><ChevronLeft aria-hidden="true" /> My trips</Link></header>
        <ol className="trip-wizard-progress" aria-label="Create trip progress">{STEPS.map((item, index) => <li key={item.key} className={index < stepIndex ? 'is-complete' : index === stepIndex ? 'is-active' : ''}><span>{index < stepIndex ? <Check aria-hidden="true" /> : `0${index + 1}`}</span><div><strong>{item.label}</strong><small>{item.caption}</small></div></li>)}</ol>
        {step === 'invitation' && <InvitationStep onContinue={() => void nextStep()} />}
        {step === 'details' && <DetailsStep form={form} errors={errors} duplicateWarning={duplicateWarning} isCheckingDuplicates={isCheckingDuplicates} onChange={updateField} onBack={() => setStep('invitation')} onContinue={() => void nextStep()} />}
        {step === 'review' && <ReviewStep input={tripInput} preview={preview} isGenerating={isGenerating} isSaving={isSaving} error={apiError} draftUndo={draftUndo} onBack={() => setStep('details')} onGenerate={() => void generatePreview()} onGenerateBlank={generateBlankItinerary} onSave={() => void saveTrip()} onUpdateDay={updateDraftDay} onUpdateActivity={updateDraftActivity} onAddActivity={addDraftActivity} onRemoveActivity={removeDraftActivity} onUndoRemoval={undoDraftRemoval} />}
      </div>
    </WorkspaceShell>
  )
}

function InvitationStep({ onContinue }: { onContinue: () => void }) {
  return <section className="wizard-stage invitation-stage"><div className="wizard-stage-intro"><p className="eyebrow"><UsersRound aria-hidden="true" /> Share from the start</p><h2>Who is planning this trip with you?</h2><p>Trip invitations will be added in the next iteration. For now, start the plan and invite teammates after the shared workspace is ready.</p><span className="wizard-note">You can skip this step without losing any trip details.</span></div><div className="wizard-panel invitation-placeholder"><span><UsersRound aria-hidden="true" /></span><h3>Invitations are coming next</h3><p>This plan stays private to you while you choose the route and preferences.</p><div className="wizard-actions"><button data-testid="trip-invitation-continue" className="dashboard-create-button" type="button" onClick={onContinue}>Continue to details <ArrowRight aria-hidden="true" /></button></div></div></section>
}

function DetailsStep({ form, errors, duplicateWarning, isCheckingDuplicates, onChange, onBack, onContinue }: { form: TripFormValues; errors: Partial<Record<'destination' | 'start_date' | 'end_date' | 'group_size' | 'budget', string>>; duplicateWarning: string | null; isCheckingDuplicates: boolean; onChange: <K extends keyof TripFormValues>(field: K, value: TripFormValues[K]) => void; onBack: () => void; onContinue: () => void }) {
  return <section className="wizard-stage details-stage"><div className="wizard-stage-intro"><p className="eyebrow"><MapPinned aria-hidden="true" /> Trip details</p><h2>Give Wandora the shape of your journey.</h2><p>Choose the timing and priorities the first draft should protect. These preferences stay visible when your group reviews the route.</p></div><div data-testid="trip-creation-form" className="wizard-panel"><div className="trip-form-grid"><FormField label="Destination *" error={errors.destination}><input data-testid="trip-destination" value={form.destination} onChange={(event) => onChange('destination', event.target.value)} placeholder="e.g. Da Nang, Hoi An & Hue" /></FormField><FormField label="Budget (optional)" error={errors.budget}><input data-testid="trip-budget" type="number" min="0" step="1" value={form.budget} onChange={(event) => onChange('budget', event.target.value)} placeholder="Amount for the group" /></FormField><FormField label="Start date *" error={errors.start_date}><input data-testid="trip-start-date" type="date" value={form.start_date} onChange={(event) => onChange('start_date', event.target.value)} /></FormField><FormField label="End date *" error={errors.end_date}><input data-testid="trip-end-date" type="date" value={form.end_date} onChange={(event) => onChange('end_date', event.target.value)} /></FormField><FormField label="Travelers *" error={errors.group_size}><input data-testid="trip-capacity" type="number" min="1" step="1" value={form.group_size} onChange={(event) => onChange('group_size', event.target.value)} /></FormField></div><PreferenceBoard form={form} onChange={onChange} /><FormField className="full-width" label="Anything else for the first draft?"><textarea value={form.notes} onChange={(event) => onChange('notes', event.target.value)} rows={3} placeholder="Dietary needs, neighbourhoods, arrival plans, or group constraints." /></FormField>{duplicateWarning && <div className="flow-error" role="alert" style={{ marginTop: '1rem', background: '#fffbeb', color: '#b45309', border: '1px solid #fcd34d', padding: '1rem', borderRadius: '0.5rem' }}><CircleAlert aria-hidden="true" /><span>{duplicateWarning}</span></div>}<div className="wizard-actions"><button className="workspace-back-link" type="button" onClick={onBack}><ArrowLeft aria-hidden="true" /> Back</button><button data-testid="trip-continue-button" className="dashboard-create-button" type="button" onClick={onContinue} disabled={isCheckingDuplicates}>{isCheckingDuplicates ? <LoaderCircle className="spin" aria-hidden="true" /> : <ArrowRight aria-hidden="true" />} {duplicateWarning ? 'Continue anyway' : 'Review your plan'}</button></div></div></section>
}

function PreferenceBoard({ form, onChange }: { form: TripFormValues; onChange: <K extends keyof TripFormValues>(field: K, value: TripFormValues[K]) => void }) {
  function toggleInterest(interest: string) { onChange('interests', form.interests.includes(interest) ? form.interests.filter((item) => item !== interest) : [...form.interests, interest]) }
  return <section className="preference-board"><div><h3>Travel preferences</h3><p>Pick the priorities Wandora should optimize while keeping the group’s constraints visible.</p></div><fieldset><legend>Pace</legend><div className="choice-chips">{PACES.map((pace) => <button type="button" className={form.pace === pace ? 'is-selected' : ''} onClick={() => onChange('pace', pace)} key={pace}>{form.pace === pace && <Check aria-hidden="true" />}{pace}</button>)}</div></fieldset><fieldset><legend>Interests</legend><div className="choice-chips">{INTERESTS.map((interest) => <button type="button" className={form.interests.includes(interest) ? 'is-selected' : ''} onClick={() => toggleInterest(interest)} key={interest}>{form.interests.includes(interest) && <Check aria-hidden="true" />}{interest}</button>)}</div></fieldset><div className="must-see-grid">{form.mustSee.map((place, index) => <label key={index}><small>Must-see {index + 1}</small><input value={place} onChange={(event) => onChange('mustSee', form.mustSee.map((item, itemIndex) => itemIndex === index ? event.target.value : item))} placeholder={index === 0 ? 'e.g. Hoi An Ancient Town' : 'Optional place'} /></label>)}<label><small>Avoid</small><input value={form.avoid} onChange={(event) => onChange('avoid', event.target.value)} placeholder="e.g. Late-night activities" /></label></div><div className="preference-insight"><Sparkles aria-hidden="true" /><div><strong>AI balance mode is on</strong><p>Wandora will balance your pace, interests, must-see places, and group budget in the first draft.</p></div></div></section>
}

function ReviewStep({ input, preview, isGenerating, isSaving, error, draftUndo, onBack, onGenerate, onGenerateBlank, onSave, onUpdateDay, onUpdateActivity, onAddActivity, onRemoveActivity, onUndoRemoval }: { input: CreateWorkspaceInput; preview: ItineraryPreview | null; isGenerating: boolean; isSaving: boolean; error: string; draftUndo: DraftUndo | null; onBack: () => void; onGenerate: () => void; onGenerateBlank: () => void; onSave: () => void; onUpdateDay: (dayIndex: number, field: 'title' | 'summary', value: string) => void; onUpdateActivity: (dayIndex: number, activityIndex: number, field: 'title' | 'start_time' | 'end_time' | 'location_name', value: string) => void; onAddActivity: (dayIndex: number, activity: GeneratedActivity) => void; onRemoveActivity: (dayIndex: number, activityIndex: number) => void; onUndoRemoval: () => void }) {
  return <section className="wizard-stage review-stage"><div className="wizard-stage-intro"><p className="eyebrow"><Compass aria-hidden="true" /> Review and draft</p><h2>Check the brief, then let AI map the first route.</h2><p>You can revise the draft here before the trip is saved to your workspace.</p></div><div className="review-layout"><aside className="review-brief"><h3>{input.title}</h3><p>{input.destination}</p><dl><div><dt>When</dt><dd>{input.start_date} to {input.end_date}</dd></div><div><dt>Travelers</dt><dd>{input.group_size}</dd></div><div><dt>Invitations</dt><dd>Invite later</dd></div><div><dt>Pace</dt><dd>{input.travel_style}</dd></div></dl><button className="workspace-back-link" type="button" onClick={onBack}><PencilLine aria-hidden="true" /> Edit details</button></aside><div className="review-draft-area">{!preview && !isGenerating && !error && <div className="draft-empty"><span><Sparkles aria-hidden="true" /></span><h3>Ready for the first itinerary</h3><p>We will generate one day at a time using the preferences you just reviewed.</p><div style={{ display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center' }}><button data-testid="generate-preview-button" className="flow-submit" type="button" onClick={onGenerate}>Generate first itinerary <Sparkles aria-hidden="true" /></button><button className="recovery-link" type="button" onClick={onGenerateBlank}>Start with a blank itinerary</button></div></div>}{isGenerating && <div data-testid="ai-generation-indicator" className="draft-generating" role="status" aria-live="polite"><div className="generation-orbit"><Compass aria-hidden="true" /><i /><i /><i /></div><p className="dashboard-kicker">AI is drafting</p><h3>Turning shared preferences into a route.</h3><p>Finding the right rhythm for each day. This can take up to 25 seconds.</p><div className="draft-skeletons">{Array.from({ length: tripDayCount(input.start_date, input.end_date) }).map((_, index) => <div key={index}><span /><span /><span /></div>)}</div></div>}{error && !isGenerating && <div className="draft-empty draft-error-fallback" style={{ background: 'var(--color-surface-dim)', borderColor: 'var(--color-border-strong)' }}><span style={{ color: 'var(--color-destructive, #ef4444)', background: '#fee2e2' }}><CircleAlert aria-hidden="true" /></span><h3 style={{ color: 'var(--color-destructive, #ef4444)' }}>AI generation failed</h3><p>{error}</p><div style={{ display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center', marginTop: '1rem' }}><button className="dashboard-create-button" type="button" onClick={onGenerate}>Try generating again</button><button className="recovery-link" type="button" onClick={onGenerateBlank}>Start with a blank itinerary</button></div></div>}{preview && <DraftEditorEnhanced preview={preview} isSaving={isSaving} draftUndo={draftUndo} onGenerate={onGenerate} onSave={onSave} onUpdateDay={onUpdateDay} onUpdateActivity={onUpdateActivity} onAddActivity={onAddActivity} onRemoveActivity={onRemoveActivity} onUndoRemoval={onUndoRemoval} />}</div></div></section>
}

export function DraftEditor({ preview, isSaving, onGenerate, onSave, onUpdateDay, onUpdateActivity }: { preview: ItineraryPreview; isSaving: boolean; onGenerate: () => void; onSave: () => void; onUpdateDay: (dayIndex: number, field: 'title' | 'summary', value: string) => void; onUpdateActivity: (dayIndex: number, activityIndex: number, field: 'title' | 'start_time' | 'end_time' | 'location_name', value: string) => void }) {
  return <div className="draft-editor"><div className="draft-editor-heading"><div><span className={`generation-source generation-source-${preview.source}`}>{preview.source === 'gemini' ? 'Generated with Gemini' : 'Fallback itinerary'}</span><h3>Your first route is ready.</h3><p>Edit any stop before this plan becomes shared.</p></div><button className="recovery-link" type="button" onClick={onGenerate}>Generate another draft</button></div><div className="draft-day-list">{preview.draft.days.map((day) => <DraftDayCard key={day.day_index} day={day} onUpdateDay={onUpdateDay} onUpdateActivity={onUpdateActivity} />)}</div><button data-testid="save-trip-button" className="flow-submit" type="button" onClick={onSave} disabled={isSaving}>{isSaving ? <><LoaderCircle className="spin" aria-hidden="true" /> Saving shared trip…</> : <>Create and save trip <Check aria-hidden="true" /></>}</button></div>
}

function DraftDayCard({ day, onUpdateDay, onUpdateActivity }: { day: GeneratedItineraryDay; onUpdateDay: (dayIndex: number, field: 'title' | 'summary', value: string) => void; onUpdateActivity: (dayIndex: number, activityIndex: number, field: 'title' | 'start_time' | 'end_time' | 'location_name', value: string) => void }) {
  return <article className="draft-day-card"><header><span>Day {day.day_index} · {formatDay(day.travel_date)}</span><input value={day.title} onChange={(event) => onUpdateDay(day.day_index, 'title', event.target.value)} aria-label={`Day ${day.day_index} title`} /></header><input className="draft-day-summary" value={day.summary ?? ''} onChange={(event) => onUpdateDay(day.day_index, 'summary', event.target.value)} placeholder="Day summary" aria-label={`Day ${day.day_index} summary`} /><ol>{day.activities.map((activity, index) => <li key={`${day.day_index}-${index}`}><div className="draft-time-fields"><input type="time" value={activity.start_time ?? ''} onChange={(event) => onUpdateActivity(day.day_index, index, 'start_time', event.target.value)} /><span>–</span><input type="time" value={activity.end_time ?? ''} onChange={(event) => onUpdateActivity(day.day_index, index, 'end_time', event.target.value)} /></div><input value={activity.title} onChange={(event) => onUpdateActivity(day.day_index, index, 'title', event.target.value)} aria-label="Activity title" /><input value={activity.location_name ?? ''} onChange={(event) => onUpdateActivity(day.day_index, index, 'location_name', event.target.value)} placeholder="Location" aria-label="Activity location" /></li>)}</ol></article>
}

function DraftEditorEnhanced({ preview, isSaving, draftUndo, onGenerate, onSave, onUpdateDay, onUpdateActivity, onAddActivity, onRemoveActivity, onUndoRemoval }: { preview: ItineraryPreview; isSaving: boolean; draftUndo: DraftUndo | null; onGenerate: () => void; onSave: () => void; onUpdateDay: (dayIndex: number, field: 'title' | 'summary', value: string) => void; onUpdateActivity: (dayIndex: number, activityIndex: number, field: 'title' | 'start_time' | 'end_time' | 'location_name', value: string) => void; onAddActivity: (dayIndex: number, activity: GeneratedActivity) => void; onRemoveActivity: (dayIndex: number, activityIndex: number) => void; onUndoRemoval: () => void }) {
  return <div className="draft-editor"><div className="draft-editor-heading"><div><span className={`generation-source generation-source-${preview.source}`}>{preview.source === 'gemini' ? 'Generated with Gemini' : 'Fallback itinerary'}</span><h3>Your first route is ready.</h3><p>Edit, add, or remove stops before this plan becomes shared.</p></div><button className="recovery-link" type="button" onClick={onGenerate}>Generate another draft</button></div><div className="draft-day-list">{preview.draft.days.map((day) => <DraftDayCardEnhanced key={day.day_index} day={day} onUpdateDay={onUpdateDay} onUpdateActivity={onUpdateActivity} onAddActivity={onAddActivity} onRemoveActivity={onRemoveActivity} />)}</div>{draftUndo && <div className="activity-undo" role="status"><span>Activity removed.</span><button type="button" onClick={onUndoRemoval}><Undo2 aria-hidden="true" /> Undo</button></div>}<button data-testid="save-trip-button" className="flow-submit" type="button" onClick={onSave} disabled={isSaving}>{isSaving ? <><LoaderCircle className="spin" aria-hidden="true" /> Saving shared trip...</> : <>Create and save trip <Check aria-hidden="true" /></>}</button></div>
}

function DraftDayCardEnhanced({ day, onUpdateDay, onUpdateActivity, onAddActivity, onRemoveActivity }: { day: GeneratedItineraryDay; onUpdateDay: (dayIndex: number, field: 'title' | 'summary', value: string) => void; onUpdateActivity: (dayIndex: number, activityIndex: number, field: 'title' | 'start_time' | 'end_time' | 'location_name', value: string) => void; onAddActivity: (dayIndex: number, activity: GeneratedActivity) => void; onRemoveActivity: (dayIndex: number, activityIndex: number) => void }) {
  const [isAdding, setIsAdding] = useState(false)
  const [title, setTitle] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [location, setLocation] = useState('')
  const [formError, setFormError] = useState('')

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!title.trim() || !startTime || !endTime) return setFormError('Add a name, start time, and end time.')
    if (endTime <= startTime) return setFormError('End time must be after start time.')
    onAddActivity(day.day_index, { title: title.trim(), start_time: startTime, end_time: endTime, location_name: location.trim() || null, activity_type: null, notes: null, external_url: null })
    setTitle('')
    setStartTime('')
    setEndTime('')
    setLocation('')
    setFormError('')
    setIsAdding(false)
  }

  return <article className="draft-day-card"><header><span>Day {day.day_index} - {formatDay(day.travel_date)}</span><input value={day.title} onChange={(event) => onUpdateDay(day.day_index, 'title', event.target.value)} aria-label={`Day ${day.day_index} title`} /></header><input className="draft-day-summary" value={day.summary ?? ''} onChange={(event) => onUpdateDay(day.day_index, 'summary', event.target.value)} placeholder="Day summary" aria-label={`Day ${day.day_index} summary`} /><ol>{day.activities.map((activity, index) => <li key={`${day.day_index}-${index}`}><div className="draft-time-fields"><input type="time" value={activity.start_time ?? ''} onChange={(event) => onUpdateActivity(day.day_index, index, 'start_time', event.target.value)} /><span>-</span><input type="time" value={activity.end_time ?? ''} onChange={(event) => onUpdateActivity(day.day_index, index, 'end_time', event.target.value)} /></div><input value={activity.title} onChange={(event) => onUpdateActivity(day.day_index, index, 'title', event.target.value)} aria-label="Activity title" /><input value={activity.location_name ?? ''} onChange={(event) => onUpdateActivity(day.day_index, index, 'location_name', event.target.value)} placeholder="Location" aria-label="Activity location" /><button className="activity-icon-button" type="button" aria-label={`Remove ${activity.title}`} title="Remove activity" onClick={() => onRemoveActivity(day.day_index, index)}><Trash2 aria-hidden="true" /></button></li>)}</ol>{!isAdding && <button className="draft-add-activity" type="button" onClick={() => setIsAdding(true)}><Plus aria-hidden="true" /> Add activity</button>}{isAdding && <form className="draft-add-form" onSubmit={submit}><input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Activity name" aria-label="New activity name" autoFocus /><input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} aria-label="New activity start time" /><input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} aria-label="New activity end time" /><input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Location (optional)" aria-label="New activity location" />{formError && <p className="form-error" role="alert">{formError}</p>}<div><button className="dashboard-create-button" type="submit"><Plus aria-hidden="true" /> Add</button><button className="recovery-link" type="button" onClick={() => { setIsAdding(false); setFormError('') }}>Cancel</button></div></form>}</article>
}

function hasValidDraftActivities(preview: ItineraryPreview) {
  return preview.draft.days.every((day) => day.activities.every((activity) => Boolean(activity.title.trim() && activity.start_time && activity.end_time && activity.end_time > activity.start_time)))
}

function buildTripInput(form: TripFormValues, groupSize: number): CreateWorkspaceInput {
  const preferenceNotes = [`Pace: ${form.pace}`, form.interests.length ? `Interests: ${form.interests.join(', ')}` : '', form.mustSee.filter(Boolean).length ? `Must-see places: ${form.mustSee.filter(Boolean).join(', ')}` : '', form.avoid.trim() ? `Avoid: ${form.avoid.trim()}` : '', form.notes.trim()].filter(Boolean).join('\n')
  return { title: `Trip to ${form.destination.trim() || 'your destination'}`, destination: form.destination.trim(), start_date: form.start_date, end_date: form.end_date, group_size: groupSize, budget: form.budget ? Number(form.budget) : undefined, travel_style: form.pace, notes: preferenceNotes || undefined }
}

function tripDayCount(startDate: string, endDate: string) {
  if (!startDate || !endDate) return 1
  return Math.max(1, Math.round((new Date(`${endDate}T00:00:00`).getTime() - new Date(`${startDate}T00:00:00`).getTime()) / 86400000) + 1)
}
