import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useOutletContext, useParams } from 'react-router'
import { Check, CircleAlert, LoaderCircle, Plus, Sparkles, Trash2, Luggage } from 'lucide-react'

import { packingApi, type PackingItem, collaborationApi, type WorkspaceMember, type Workspace } from '@/lib/api'

export function PackingTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>()
  const { workspaceId = '' } = useParams()
  
  const [items, setItems] = useState<PackingItem[]>([])
  const [members, setMembers] = useState<WorkspaceMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  
  const [newItemName, setNewItemName] = useState('')
  const [isAdding, setIsAdding] = useState(false)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const [fetchedItems, fetchedMembers] = await Promise.all([
        packingApi.listItems(workspaceId),
        collaborationApi.listMembers(workspaceId)
      ])
      setItems(fetchedItems)
      setMembers(fetchedMembers)
    } catch (e) {
      setError('Could not load packing list.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  useEffect(() => { void loadData() }, [loadData])

  async function generateAI() {
    setIsGenerating(true)
    setError('')
    try {
      await packingApi.generateSuggestions(workspaceId)
      await loadData()
    } catch (e) {
      setError('Could not generate packing list.')
    } finally {
      setIsGenerating(false)
    }
  }

  async function toggleItem(item: PackingItem) {
    try {
      const assignment = item.assignments?.[0]
      const isChecked = assignment ? !assignment.is_checked : true
      if (assignment) {
        const updated = await packingApi.assignItem(item.id, { user_id: assignment.user_id, is_checked: isChecked })
        setItems(items.map(i => i.id === updated.id ? updated : i))
      } else {
        // Must assign to someone to check it off. If not assigned, assign to current user or first member.
        const userId = members.length > 0 ? members[0].user_id : workspace.owner_id
        if (userId) {
          const updated = await packingApi.assignItem(item.id, { user_id: userId, is_checked: true })
          setItems(items.map(i => i.id === updated.id ? updated : i))
        }
      }
    } catch (e) {
      // Ignore
    }
  }

  async function deleteItem(itemId: string) {
    try {
      await packingApi.deleteItem(itemId)
      setItems(items.filter(i => i.id !== itemId))
    } catch (e) {
      // Ignore
    }
  }

  async function assignItem(itemId: string, userId: string | null) {
    try {
      if (!userId) return // Backend currently doesn't support unassigning easily via this endpoint
      const updated = await packingApi.assignItem(itemId, { user_id: userId, is_checked: false })
      setItems(items.map(i => i.id === updated.id ? updated : i))
    } catch (e) {
      // Ignore
    }
  }

  async function addItem(e: FormEvent) {
    e.preventDefault()
    if (!newItemName.trim()) return
    setIsAdding(true)
    try {
      const added = await packingApi.addItem(workspaceId, { name: newItemName.trim() })
      setItems([...items, added])
      setNewItemName('')
    } catch (e) {
      setError('Could not add item.')
    } finally {
      setIsAdding(false)
    }
  }

  if (isLoading) return <section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading packing list…</p></section>

  return (
    <div className="workspace-view">
      <style>{`
        .packing-row {
          background: var(--color-surface);
          border-radius: 0.75rem;
          padding: 0.85rem 1.25rem;
          border: 1px solid var(--color-border);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .packing-row:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.05);
        }
        .bento-input {
          padding: 0.65rem 0.75rem;
          border-radius: 0.5rem;
          border: 1px solid var(--color-border);
          background-color: var(--color-surface-dim);
          transition: box-shadow 0.2s ease, border-color 0.2s ease;
          font-family: inherit;
          font-size: 0.95rem;
          color: var(--color-text);
        }
        .bento-input:focus {
          outline: none;
          box-shadow: 0 0 0 2px var(--color-brand);
          border-color: transparent;
        }
        .assign-select {
          padding: 0.4rem 0.75rem;
          border-radius: 9999px; /* Pill shape */
          border: 1px solid var(--color-border);
          background-color: var(--color-surface-dim);
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--color-text);
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .assign-select:hover {
          border-color: var(--color-brand-muted);
        }
        .checkbox-btn {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: 2px solid var(--color-text-dim);
          background: var(--color-surface);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          flex-shrink: 0;
          box-shadow: 0 1px 2px rgba(0,0,0,0.05) inset;
        }
        .checkbox-btn.checked {
          background: var(--color-brand);
          border-color: var(--color-brand);
          opacity: 1;
        }
        .checkbox-btn:not(.checked):hover {
          opacity: 1;
          border-color: var(--color-brand);
        }
        .action-btn {
          opacity: 0.4;
          transition: opacity 0.2s ease, color 0.2s ease;
          cursor: pointer;
          background: transparent;
          border: none;
          color: var(--color-destructive, #ef4444);
          padding: 0.5rem;
          border-radius: 0.375rem;
        }
        .action-btn:hover {
          opacity: 1;
          background: var(--color-surface-dim);
        }
      `}</style>

      <header className="workspace-view-header">
        <div>
          <h2>Group Packing List</h2>
          <p>Shared items and personal responsibilities</p>
        </div>
        <button className="button button-primary" type="button" onClick={() => void generateAI()} disabled={isGenerating} style={{ padding: '0.6rem 1.25rem', borderRadius: '9999px', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
          {isGenerating ? <><LoaderCircle className="spin" aria-hidden="true" size={18} /> Generating…</> : <><Sparkles aria-hidden="true" size={18} /> Generate AI Checklist</>}
        </button>
      </header>
      
      {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span></div>}

      <div className="packing-list-container" style={{ marginTop: '2rem' }}>
        <form onSubmit={addItem} style={{ display: 'flex', gap: '1rem', marginBottom: '2.5rem' }}>
          <input 
            className="bento-input"
            value={newItemName} 
            onChange={e => setNewItemName(e.target.value)} 
            placeholder="Add a custom item (e.g., Sunscreen, Passports)..." 
            style={{ flex: 1, padding: '0.85rem 1rem', fontSize: '1rem' }}
            disabled={isAdding}
          />
          <button className="button button-secondary" type="submit" disabled={isAdding || !newItemName.trim()} style={{ borderRadius: '0.5rem', padding: '0 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {isAdding ? <LoaderCircle className="spin" aria-hidden="true" size={18} /> : <Plus aria-hidden="true" size={18} />} Add
          </button>
        </form>

        {items.length === 0 ? (
          <div className="packing-list-empty" style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--color-surface-dim)', borderRadius: '1rem', border: '2px dashed var(--color-border)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <Luggage size={48} color="var(--color-text-dim)" strokeWidth={1.5} />
            <div style={{ maxWidth: '350px' }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--color-text)', fontSize: '1.25rem' }}>Your suitcase is empty!</h3>
              <p style={{ margin: '0 0 1.5rem 0', color: 'var(--color-text-dim)', fontSize: '0.95rem' }}>Start adding items manually or let our AI generate a personalized checklist for your trip.</p>
              <button className="button button-primary" type="button" onClick={() => void generateAI()} disabled={isGenerating} style={{ borderRadius: '9999px', padding: '0.6rem 1.25rem', width: '100%', justifyContent: 'center' }}>
                {isGenerating ? <><LoaderCircle className="spin" aria-hidden="true" size={18} /> Generating…</> : <><Sparkles aria-hidden="true" size={18} /> Generate AI Checklist</>}
              </button>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', width: '100%' }}>
            {/* Active Items */}
            {items.filter(i => !i.assignments?.[0]?.is_checked).length > 0 && (
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%', alignItems: 'stretch' }}>
                {items.filter(i => !i.assignments?.[0]?.is_checked).map(item => {
                  const assignment = item.assignments?.[0]
                  const isChecked = false
                  const assigneeId = assignment ? String(assignment.user_id) : ''
                  
                  return (
                    <li key={item.id} className="packing-row">
                      <button 
                        type="button" 
                        onClick={() => void toggleItem(item)}
                        className={`checkbox-btn ${isChecked ? 'checked' : ''}`}
                        title={isChecked ? "Mark as uncompleted" : "Mark as completed"}
                      >
                        {isChecked && <Check size={14} strokeWidth={3} />}
                      </button>
                      <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1.05rem', textDecoration: isChecked ? 'line-through' : 'none', color: isChecked ? 'var(--color-text-dim)' : 'var(--color-text)', transition: 'color 0.2s ease', fontWeight: isChecked ? 400 : 500 }}>
                          {item.name}
                        </span>
                        {item.category && (
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.2rem 0.5rem', borderRadius: '4px', background: 'var(--color-surface-dim)', color: 'var(--color-text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            {item.category}
                          </span>
                        )}
                      </div>
                      
                      <select 
                        value={assigneeId} 
                        onChange={(e) => void assignItem(item.id, e.target.value || null)}
                        className="assign-select"
                        title="Assign to a member"
                      >
                        <option value="">Unassigned</option>
                        {members.map(m => (
                          <option key={m.user_id} value={m.user_id}>{m.user_full_name || m.user_email || 'Unknown User'}</option>
                        ))}
                      </select>
                      
                      <button type="button" onClick={() => void deleteItem(item.id)} className="action-btn" title="Delete item">
                        <Trash2 size={18} />
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}

            {/* Completed Items */}
            {items.filter(i => i.assignments?.[0]?.is_checked).length > 0 && (
              <div>
                <h3 style={{ fontSize: '1rem', color: 'var(--color-text-dim)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  Completed ({items.filter(i => i.assignments?.[0]?.is_checked).length})
                </h3>
                <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%', alignItems: 'stretch' }}>
                  {items.filter(i => i.assignments?.[0]?.is_checked).map(item => {
                    const assignment = item.assignments?.[0]
                    const isChecked = true
                    const assigneeId = assignment ? String(assignment.user_id) : ''
                    
                    return (
                      <li key={item.id} className="packing-row" style={{ opacity: 0.7 }}>
                        <button 
                          type="button" 
                          onClick={() => void toggleItem(item)}
                          className={`checkbox-btn ${isChecked ? 'checked' : ''}`}
                          title={isChecked ? "Mark as uncompleted" : "Mark as completed"}
                        >
                          {isChecked && <Check size={14} strokeWidth={3} />}
                        </button>
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontSize: '1.05rem', textDecoration: isChecked ? 'line-through' : 'none', color: isChecked ? 'var(--color-text-dim)' : 'var(--color-text)', transition: 'color 0.2s ease', fontWeight: isChecked ? 400 : 500 }}>
                            {item.name}
                          </span>
                          {item.category && (
                            <span style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.2rem 0.5rem', borderRadius: '4px', background: 'var(--color-surface-dim)', color: 'var(--color-text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                              {item.category}
                            </span>
                          )}
                        </div>
                        
                        <select 
                          value={assigneeId} 
                          onChange={(e) => void assignItem(item.id, e.target.value || null)}
                          className="assign-select"
                          title="Assign to a member"
                        >
                          <option value="">Unassigned</option>
                          {members.map(m => (
                            <option key={m.user_id} value={m.user_id}>{m.user_full_name || m.user_email || 'Unknown User'}</option>
                          ))}
                        </select>
                        
                        <button type="button" onClick={() => void deleteItem(item.id)} className="action-btn" title="Delete item">
                          <Trash2 size={18} />
                        </button>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
