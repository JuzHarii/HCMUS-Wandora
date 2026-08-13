import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router'

import { clearAccessToken, getAccessToken, saveAccessToken } from '@/lib/auth-storage'
import { getCurrentUser, login, signUp, type AuthSession, type AuthUser } from '@/lib/api'

type AuthContextValue = {
  user: AuthUser | null
  isLoading: boolean
  signUp: (payload: { full_name: string; email: string; password: string }) => Promise<void>
  login: (payload: { email: string; password: string }) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function persist(session: AuthSession, setUser: (user: AuthUser) => void) {
  saveAccessToken(session.access_token)
  setUser(session.user)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      setIsLoading(false)
      return
    }
    void getCurrentUser()
      .then(setUser)
      .catch(() => clearAccessToken())
      .finally(() => setIsLoading(false))
  }, [])

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isLoading,
    signUp: async (payload) => persist(await signUp(payload), setUser),
    login: async (payload) => persist(await login(payload), setUser),
    logout: () => {
      clearAccessToken()
      setUser(null)
    },
  }), [isLoading, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) throw new Error('useAuth must be used within AuthProvider.')
  return context
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return null
  if (!user) return <Navigate replace to={`/auth?mode=login&next=${encodeURIComponent(location.pathname)}`} />
  return children
}
