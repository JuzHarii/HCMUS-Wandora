import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { ArrowLeft, Check, CircleAlert, ClipboardList, LoaderCircle, Plus, UsersRound } from 'lucide-react'
import { Link, useParams } from 'react-router'

import { WorkspaceShell } from '@/components/layout/WorkspaceShell'
import { createPackingItem, getTripOverview, listPackingItems, updatePackingItem, type PackingItem, type Workspace } from '@/lib/api'

export function PackingPage() {
  const { workspaceId } = useParams()
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [items, setItems] = useState<PackingItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAdding, setIsAdding] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!workspaceId) return
    setIsLoading(true)
    setError('')
    try {
      const [overview, nextItems] = await Promise.all([getTripOverview(workspaceId), listPackingItems(workspaceId)])
      setWorkspace(overview.workspace)
      setItems(nextItems)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Could not load the packing list.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  useEffect(() => { void load() }, [load])

  async function toggleItem(item: PackingItem) {
    try {
      const updated = await updatePackingItem(item.id, { is_completed: !item.is_completed })
      setItems((current) => current.map((candidate) => candidate.id === updated.id ? updated : candidate))
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : 'Could not update this item.')
    }
  }

  const completeCount = items.filter((item) => item.is_completed).length

  return (
    <WorkspaceShell>
      <div className="workspace-view packing-view">
        <header className="workspace-view-header"><div><p className="dashboard-kicker">Trip preparation</p><h1>Pack with the whole group.</h1><p className="packing-subtitle">{workspace ? `${workspace.title} - ${workspace.destination}` : 'Shared packing list'}</p></div>{workspaceId && <Link className="workspace-back-link" to={`/trips/${workspaceId}`}><ArrowLeft aria-hidden="true" /> Itinerary</Link>}</header>
        {isLoading && <section className="packing-empty"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading shared checklist...</p></section>}
        {!isLoading && error && <section className="flow-error" role="alert"><CircleAlert aria-hidden="true" /> <span>{error}</span><button type="button" className="recovery-link" onClick={() => void load()}>Try again</button></section>}
        {!isLoading && !error && <><section className="packing-summary"><div><span>{completeCount}/{items.length}</span><p>items ready</p></div><i aria-hidden="true"><b style={{ width: `${items.length ? Math.round((completeCount / items.length) * 100) : 0}%` }} /></i><button className="dashboard-create-button" type="button" onClick={() => setIsAdding(true)}><Plus aria-hidden="true" /> Add item</button></section>
        {isAdding && workspaceId && <PackingForm workspaceId={workspaceId} onCancel={() => setIsAdding(false)} onCreated={(item) => { setItems((current) => [item, ...current]); setIsAdding(false) }} onError={setError} />}
        {items.length === 0 ? <section className="packing-empty"><ClipboardList aria-hidden="true" /><h2>Nothing to pack yet.</h2><p>Add the first item so the group can see what still needs attention.</p><button className="dashboard-create-button" type="button" onClick={() => setIsAdding(true)}>Add item</button></section> : <ol className="packing-list">{items.map((item) => <li key={item.id} className={item.is_completed ? 'is-complete' : ''}><button className="packing-check" type="button" aria-label={`Mark ${item.name} ${item.is_completed ? 'not ready' : 'ready'}`} onClick={() => void toggleItem(item)}>{item.is_completed && <Check aria-hidden="true" />}</button><div><strong>{item.name}</strong><p>{item.quantity > 1 ? `${item.quantity} pieces` : '1 piece'}{item.assigned_to ? ` - ${item.assigned_to}` : ''}{item.note ? ` - ${item.note}` : ''}</p></div><span>{item.assigned_to ? <><UsersRound aria-hidden="true" /> Assigned</> : 'Unassigned'}</span></li>)}</ol>}</>}
      </div>
    </WorkspaceShell>
  )
}

function PackingForm({ workspaceId, onCancel, onCreated, onError }: { workspaceId: string; onCancel: () => void; onCreated: (item: PackingItem) => void; onError: (message: string) => void }) {
  const [name, setName] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [assignedTo, setAssignedTo] = useState('')
  const [note, setNote] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!name.trim()) return onError('Enter a packing item name.')
    setIsSaving(true)
    onError('')
    try {
      onCreated(await createPackingItem(workspaceId, { name: name.trim(), quantity: Number(quantity), assigned_to: assignedTo.trim() || null, note: note.trim() || null }))
    } catch (saveError) {
      onError(saveError instanceof Error ? saveError.message : 'Could not add this item.')
    } finally {
      setIsSaving(false)
    }
  }

  return <form className="packing-form" onSubmit={submit}><label>Item<input autoFocus value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Sunscreen" /></label><label>Quantity<input type="number" min="1" max="99" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label><label>Assigned to<input value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)} placeholder="Optional member" /></label><label>Note<input value={note} onChange={(event) => setNote(event.target.value)} placeholder="Optional detail" /></label><div><button className="dashboard-create-button" type="submit" disabled={isSaving}>{isSaving ? <LoaderCircle className="spin" aria-hidden="true" /> : <Plus aria-hidden="true" />} Add item</button><button className="workspace-back-link" type="button" onClick={onCancel} disabled={isSaving}>Cancel</button></div></form>
}
