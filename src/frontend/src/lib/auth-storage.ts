const TOKEN_KEY = 'wandora_access_token'

export function getAccessToken() {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function saveAccessToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearAccessToken() {
  window.localStorage.removeItem(TOKEN_KEY)
}
