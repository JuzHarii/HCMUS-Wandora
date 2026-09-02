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
  const isOwner = workspace.current_user_role?.toLowerCase() === 'owner'

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
      <style>{`
        .bento-card {
          background: var(--color-surface);
          border-radius: 1rem;
          padding: 1.25rem 1.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
          border: 1px solid var(--color-border);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
          display: flex;
          align-items: center;
          gap: 1.25rem;
        }
        .bento-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
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
        .bento-sidebar {
          background: var(--color-surface);
          padding: 1.75rem;
          border-radius: 1rem;
          height: fit-content;
          position: sticky;
          top: 2rem;
          box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.05);
          border: 1px solid var(--color-border);
        }
        .avatar-circle {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--color-brand) 0%, #a855f7 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 1.1rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          flex-shrink: 0;
        }
        .role-pill {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.8rem;
          font-weight: 600;
          background: var(--color-surface-dim);
          color: var(--color-text);
          border: 1px solid var(--color-border);
        }
        .role-pill.owner {
          background: var(--color-brand-muted);
          color: var(--color-brand);
          border-color: var(--color-brand-muted);
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
          <h2>Members & Roles</h2>
          <p>Manage who can view or edit this trip</p>
        </div>
      </header>
      
      {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span></div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2.5rem', marginTop: '2rem' }}>
        <div className="members-list">
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {members.map(member => (
              <li key={member.user_id} className="bento-card">
                <div className="avatar-circle">
                  {member.user_full_name?.charAt(0).toUpperCase() || member.user_email?.charAt(0).toUpperCase() || '?'}
                </div>
                <div style={{ flex: 1 }}>
                  <strong style={{ fontSize: '1.1rem', display: 'block', marginBottom: '0.1rem', color: 'var(--color-text)' }}>{member.user_full_name || 'Unknown User'}</strong>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text-dim)' }}>{member.user_email}</p>
                </div>
                
                {member.role?.toLowerCase() === 'owner' ? (
                  <span className="role-pill owner"><Shield size={14} /> Owner</span>
                ) : (
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    {isOwner ? (
                      <select 
                        value={member.role?.toLowerCase()} 
                        onChange={(e) => void changeRole(member.user_id, e.target.value)}
                        className="bento-input"
                        style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
                      >
                        <option value="editor">Editor</option>
                        <option value="viewer">Viewer</option>
                      </select>
                    ) : (
                      <span className="role-pill">{member.role}</span>
                    )}
                    {isOwner && (
                      <button type="button" onClick={() => void removeMember(member.user_id)} className="action-btn" title="Remove member">
                        <Trash2 size={18} />
                      </button>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
        
        {isOwner ? (
          <aside className="bento-sidebar">
            <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem', fontWeight: 600 }}>Invite a member</h3>
            <form onSubmit={inviteMember} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
                Email address
                <input type="email" className="bento-input" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} required placeholder="colleague@example.com" />
              </label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
                Role
                <select className="bento-input" value={inviteRole} onChange={e => setInviteRole(e.target.value)}>
                  <option value="editor">Editor (Can edit itinerary)</option>
                  <option value="viewer">Viewer (Read-only & vote)</option>
                </select>
              </label>
              <button className="button button-primary" type="submit" disabled={isInviting || !inviteEmail.trim()} style={{ marginTop: '0.5rem', padding: '0.75rem', borderRadius: '0.5rem' }}>
                {isInviting ? <LoaderCircle className="spin" aria-hidden="true" /> : <UserPlus aria-hidden="true" size={18} />} Send Invite
              </button>
            </form>
          </aside>
        ) : (
          <aside className="bento-sidebar" style={{ background: 'var(--color-surface-dim)', boxShadow: 'none', border: '1px dashed var(--color-border)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '1rem', padding: '1rem 0' }}>
              <Shield size={32} color="var(--color-text-dim)" strokeWidth={1.5} />
              <p style={{ margin: 0, color: 'var(--color-text-dim)', fontSize: '0.95rem' }}>Only Trip Owner can manage member invitations.</p>
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}
