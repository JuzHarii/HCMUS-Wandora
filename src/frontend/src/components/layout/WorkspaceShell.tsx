import type { ReactNode } from 'react'
import { Compass, LayoutGrid, Luggage } from 'lucide-react'
import { Link, useLocation } from 'react-router'

import { useAuth } from '@/auth'

type WorkspaceShellProps = {
  children: ReactNode
}

export function WorkspaceShell({ children }: WorkspaceShellProps) {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const isTripsPage = pathname === '/home'
  const workspaceMatch = pathname.match(/^\/trips\/([^/]+)/)
  const workspaceId = workspaceMatch?.[1]
  const isPackingPage = pathname.endsWith('/packing')

  return (
    <main className="dashboard-page workspace-shell">
      <aside className="dashboard-sidebar" aria-label="Trip workspace navigation">
        <Link className="dashboard-brand" to="/home"><span className="dashboard-mark" aria-hidden="true"><Compass /></span><span>Wandora<small>Travel together</small></span></Link>
        <nav className="dashboard-nav">
          <Link className={`dashboard-nav-link ${isTripsPage ? 'is-active' : ''}`} to="/home" aria-current={isTripsPage ? 'page' : undefined}><LayoutGrid aria-hidden="true" /> My trips</Link>
          {workspaceId && <Link className={`dashboard-nav-link ${isPackingPage ? 'is-active' : ''}`} to={`/trips/${workspaceId}/packing`} aria-current={isPackingPage ? 'page' : undefined}><Luggage aria-hidden="true" /> Packing</Link>}
        </nav>
        <div className="dashboard-sidebar-note"><span className="dashboard-sidebar-dot" aria-hidden="true" /><p>Each trip stays private to its invited members.</p></div>
        <div className="dashboard-user-card"><span className="dashboard-avatar">{user?.full_name.charAt(0).toUpperCase() ?? 'W'}</span><div><strong>{user?.full_name ?? 'Wandora traveler'}</strong><button data-testid="dashboard-signout" type="button" onClick={logout}>Sign out</button></div></div>
      </aside>
      <section className="dashboard-content workspace-main">{children}</section>
    </main>
  )
}
