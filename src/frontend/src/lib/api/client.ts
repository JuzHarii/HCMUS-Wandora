import { getAccessToken } from '@/lib/auth-storage'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "")

type ApiErrorPayload = { detail?: string | Array<{ msg?: string }> }

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const accessToken = getAccessToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorPayload
    const detail = Array.isArray(body.detail)
      ? body.detail.map((item) => item.msg).filter(Boolean).join(" ")
      : body.detail
    throw new Error(detail || "Không thể hoàn tất yêu cầu. Vui lòng thử lại.")
  }
  return response.json() as Promise<T>
}
