import { useState, type FormEvent } from 'react'
import { ArrowRight, CalendarPlus, ChevronLeft, CircleAlert, LoaderCircle } from 'lucide-react'
import { Link, useNavigate } from 'react-router'

import { FormField } from '@/components/forms/FormField'
import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { createWorkspace, generateItinerary, type Workspace } from '@/lib/api'

type TripFormValues = {
  destination: string
  start_date: string
  end_date: string
  group_size: string
  budget: string
  travel_style: string
  notes: string
}

export function TripCreationPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<TripFormValues>({ destination: '', start_date: '', end_date: '', group_size: '2', budget: '', travel_style: 'Balanced', notes: '' })
  const [errors, setErrors] = useState<Partial<Record<keyof TripFormValues, string>>>({})
  const [createdWorkspace, setCreatedWorkspace] = useState<Workspace | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [apiError, setApiError] = useState('')

  function updateField(field: keyof TripFormValues, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  function validate(): boolean {
    const nextErrors: Partial<Record<keyof TripFormValues, string>> = {}
    if (!form.destination.trim()) nextErrors.destination = 'Choose a destination for this trip.'
    if (!form.start_date) nextErrors.start_date = 'Choose a start date.'
    if (!form.end_date) nextErrors.end_date = 'Choose an end date.'
    if (form.start_date && form.end_date && form.end_date < form.start_date) nextErrors.end_date = 'End date must be after or equal to start date.'
    const groupSize = Number(form.group_size)
    if (!Number.isInteger(groupSize) || groupSize < 1) nextErrors.group_size = 'Enter at least 1 traveler.'
    if (form.budget && (!Number.isInteger(Number(form.budget)) || Number(form.budget) < 0)) nextErrors.budget = 'Budget must be a whole number of 0 or more.'
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  async function generateAndOpen(workspace: Workspace) {
    setIsSubmitting(true)
    setApiError('')
    try {
      await generateItinerary(workspace.id)
      navigate(`/trips/${workspace.id}`)
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Could not generate the itinerary.')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function submitForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!validate()) return
    setIsSubmitting(true)
    setApiError('')
    try {
      const workspace = await createWorkspace({
        title: `Trip to ${form.destination.trim()}`,
        destination: form.destination.trim(),
        start_date: form.start_date,
        end_date: form.end_date,
        group_size: Number(form.group_size),
        budget: form.budget ? Number(form.budget) : undefined,
        travel_style: form.travel_style || undefined,
        notes: form.notes.trim() || undefined,
      })
      setCreatedWorkspace(workspace)
      await generateAndOpen(workspace)
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Could not create this trip.')
      setIsSubmitting(false)
    }
  }

  return (
    <WorkspaceShell>
      <div className="workspace-view workspace-create-view">
        <header className="workspace-view-header"><div><p className="dashboard-kicker">New shared plan</p><h1>Start a trip</h1></div><Link className="workspace-back-link" to="/home"><ChevronLeft aria-hidden="true" /> My trips</Link></header>
        <section className="trip-flow-grid" aria-labelledby="trip-create-title">
          <aside className="flow-intro">
            <p className="eyebrow"><CalendarPlus aria-hidden="true" /> Trip details</p>
            <h1 id="trip-create-title">Give the trip a starting point.</h1>
            <p>Tell Wandora where and when you are going. We will save the shared workspace, then draft the first route for your group.</p>
            <ol className="flow-steps" aria-label="Trip planning steps"><li className="is-active"><span>01</span> Trip details</li><li><span>02</span> AI route draft</li><li><span>03</span> Review together</li></ol>
          </aside>
          <div className="trip-form-card">
            <div className="form-card-heading"><span className="status-pill" data-testid="trip-status-badge">{createdWorkspace?.status ?? 'Draft'}</span><p>Fields marked * are needed to start your plan.</p></div>
            <form data-testid="trip-creation-form" noValidate onSubmit={submitForm}>
              <div className="trip-form-grid">
                <FormField label="Destination *" error={errors.destination}><input data-testid="trip-destination" value={form.destination} onChange={(event) => updateField('destination', event.target.value)} placeholder="e.g. Da Nang, Hoi An & Hue" autoComplete="off" /></FormField>
                <FormField label="Travel style"><select data-testid="trip-style" value={form.travel_style} onChange={(event) => updateField('travel_style', event.target.value)}><option>Balanced</option><option>Cultural</option><option>Relaxed</option><option>Food focused</option><option>Adventure</option></select></FormField>
                <FormField label="Start date *" error={errors.start_date}><input data-testid="trip-start-date" type="date" value={form.start_date} onChange={(event) => updateField('start_date', event.target.value)} /></FormField>
                <FormField label="End date *" error={errors.end_date}><input data-testid="trip-end-date" type="date" value={form.end_date} onChange={(event) => updateField('end_date', event.target.value)} /></FormField>
                <FormField label="Travelers *" error={errors.group_size}><input data-testid="trip-capacity" type="number" min="1" step="1" value={form.group_size} onChange={(event) => updateField('group_size', event.target.value)} /></FormField>
                <FormField label="Budget (optional)" error={errors.budget}><input data-testid="trip-budget" type="number" min="0" step="1" value={form.budget} onChange={(event) => updateField('budget', event.target.value)} placeholder="Amount for the group" /></FormField>
                <FormField className="full-width" label="Notes for the first draft"><textarea value={form.notes} onChange={(event) => updateField('notes', event.target.value)} rows={4} placeholder="Places, pace, dietary needs, or anything the group agrees on." /></FormField>
              </div>
              {apiError && <div className="flow-error" role="alert"><CircleAlert aria-hidden="true" /><span>{apiError}</span></div>}
              {createdWorkspace && apiError ? <button className="flow-submit" type="button" onClick={() => void generateAndOpen(createdWorkspace)} disabled={isSubmitting}>{isSubmitting ? <><LoaderCircle className="spin" aria-hidden="true" /> Drafting itinerary…</> : <>Retry itinerary generation <ArrowRight aria-hidden="true" /></>}</button> : <button data-testid="trip-continue-button" className="flow-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? <><LoaderCircle className="spin" aria-hidden="true" /> <span data-testid="ai-generation-indicator">Saving trip and drafting route…</span></> : <>Create trip and draft route <ArrowRight aria-hidden="true" /></>}</button>}
            </form>
          </div>
        </section>
      </div>
    </WorkspaceShell>
  )
}
