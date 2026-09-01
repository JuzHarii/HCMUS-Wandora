import { request } from './client'
import type { AuthSession, AuthUser } from './types'

export const authApi = {
  signUp: (payload: { full_name: string; email: string; password: string }) => {
    return request<AuthSession>('/api/v1/auth/signup', { method: 'POST', body: JSON.stringify(payload) })
  },
  
  register: (payload: { full_name: string; email: string; password: string }) => {
    // Assuming backend also has /register, mapping it just in case
    return request<AuthUser>('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(payload) })
  },

  login: (payload: { email: string; password: string }) => {
    return request<AuthSession>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) })
  },

  getCurrentUser: () => {
    return request<AuthUser>('/api/v1/auth/me')
  }
}
