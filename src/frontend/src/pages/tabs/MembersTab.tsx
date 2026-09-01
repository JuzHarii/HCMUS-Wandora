import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useOutletContext, useParams } from 'react-router'
import { CircleAlert, LoaderCircle, Trash2, UserPlus, Shield } from 'lucide-react'

import { collaborationApi, type WorkspaceMember, type Workspace } from '@/lib/api'

export function MembersTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>()
  const { workspaceId = '' } = useParams()
  
  const [members, setMembers] = useState<WorkspaceMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('viewer')
  const [isInviting, setIsInviting] = useState(false)

  const loadMembers = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      setMembers(await collaborationApi.listMembers(workspaceId))
    } catch (e) {
      setError('Could not load members.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  useEffect(() => { void loadMembers() }, [loadMembers])

  async function inviteMember(e: FormEvent) {
    e.preventDefault()
    if (!inviteEmail.trim()) return
    setIsInviting(true)
    setError('')
    try {
      const added = await collaborationApi.addMember(workspaceId, { email: inviteEmail.trim(), role: inviteRole })
      setMembers([...members, added])
      setInviteEmail('')
      setInviteRole('viewer')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not invite member.')
    } finally {
      setIsInviting(false)
    }
  }

  async function changeRole(userId: string, newRole: string) {
    try {
      const updated = await collaborationApi.updateMemberRole(workspaceId, userId, { role: newRole })
      setMembers(members.map(m => m.user_id === userId ? updated : m))
    } catch (e) {
      alert('Failed to change role')
    }
  }

  async function removeMember(userId: string) {
    if (!window.confirm('Remove this member from the trip?')) return
    try {
      await collaborationApi.removeMember(workspaceId, userId)
      setMembers(members.filter(m => m.user_id !== userId))
    } catch (e) {
      alert('Failed to remove member')
    }
  }

  if (isLoading) return <section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading members…</p></section>

  return (
    <div className="workspace-view">
      <header className="workspace-view-header">
        <div>
          <h2>Members & Roles</h2>
          <p>Manage who can view or edit this trip</p>
        </div>
      </header>
      
      {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span></div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem', marginTop: '2rem' }}>
        <div className="members-list">
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {members.map(member => (
              <li key={member.user_id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', background: 'var(--color-surface-dim)', borderRadius: '0.5rem' }}>
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--color-brand)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                  {member.user_full_name?.charAt(0).toUpperCase() || member.user_email?.charAt(0).toUpperCase() || '?'}
                </div>
                <div style={{ flex: 1 }}>
                  <strong>{member.user_full_name || 'Unknown User'}</strong>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--color-text-dim)' }}>{member.user_email}</p>
                </div>
                
                {member.role?.toLowerCase() === 'owner' ? (
                  <span className="status-pill" style={{ background: 'var(--color-brand-muted)' }}><Shield size={14} style={{ marginRight: '4px' }} /> Owner</span>
                ) : (
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <select 
                      value={member.role?.toLowerCase()} 
                      onChange={(e) => void changeRole(member.user_id, e.target.value)}
                      style={{ padding: '0.25rem', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '0.85rem' }}
                    >
                      <option value="editor">Editor</option>
                      <option value="viewer">Viewer</option>
                    </select>
                    <button type="button" onClick={() => void removeMember(member.user_id)} style={{ background: 'transparent', border: 'none', color: 'var(--color-text-dim)', cursor: 'pointer' }}>
                      <Trash2 size={18} />
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
        
        <aside style={{ background: 'var(--color-surface-dim)', padding: '1.5rem', borderRadius: '0.5rem', height: 'fit-content' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Invite a member</h3>
          <form onSubmit={inviteMember} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.85rem' }}>
              Email address
              <input type="email" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} required style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)' }} />
            </label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.85rem' }}>
              Role
              <select value={inviteRole} onChange={e => setInviteRole(e.target.value)} style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
                <option value="editor">Editor (Can edit itinerary)</option>
                <option value="viewer">Viewer (Read-only & vote)</option>
              </select>
            </label>
            <button className="button button-primary" type="submit" disabled={isInviting || !inviteEmail.trim()} style={{ marginTop: '0.5rem' }}>
              {isInviting ? <LoaderCircle className="spin" aria-hidden="true" /> : <UserPlus aria-hidden="true" />} Send Invite
            </button>
          </form>
        </aside>
      </div>
    </div>
  )
}
