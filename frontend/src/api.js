// Thin wrapper around fetch for the FastAPI backend (proxied at /api).
const BASE = import.meta.env.VITE_API_URL || '/api'
const TOKEN_KEY = 'resume_analyzer_token'

// sessionStorage is cleared when the tab closes. It is still readable by any
// script on the page, so the CSP in nginx.conf blocks third-party scripts.
export const getToken = () => sessionStorage.getItem(TOKEN_KEY)
export const setToken = (token) =>
  token ? sessionStorage.setItem(TOKEN_KEY, token) : sessionStorage.removeItem(TOKEN_KEY)

let onUnauthorized = () => {}
export const setUnauthorizedHandler = (fn) => {
  onUnauthorized = fn
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

function describe(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (d.msg || 'Invalid input').replace(/^Value error, /, ''))
      .join('. ')
  }
  return 'Something went wrong. Try again.'
}

async function request(path, { method = 'GET', json, form, auth = true } = {}) {
  const headers = {}
  const token = getToken()
  if (auth && token) headers.Authorization = `Bearer ${token}`
  let body
  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  } else if (form) {
    body = form
  }

  let res
  try {
    const url = BASE === '/api'
    ? BASE + path
    : BASE.replace(/\/$/, '') + path

    res = await fetch(url, { method, headers, body })
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Check that the backend is running.')
  }
  if (res.status === 401 && auth) onUnauthorized()
  if (res.status === 204) return null

  let data = null
  try {
    data = await res.json()
  } catch {
    /* empty or non-JSON body */
  }
  if (!res.ok) throw new ApiError(res.status, describe(data?.detail))
  return data
}

export const api = {
  register: (email, password) => request('/auth/register', { method: 'POST', json: { email, password }, auth: false }),
  login: async (email, password) => {
    const form = new URLSearchParams({ username: email, password })
    const data = await request('/auth/login', { method: 'POST', form, auth: false })
    setToken(data.access_token)
  },
  me: () => request('/auth/me'),
  listDocuments: () => request('/documents'),
  uploadDocument: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/documents', { method: 'POST', form })
  },
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),
  createAnalysis: (payload) => request('/analyses', { method: 'POST', json: payload }),
  listAnalyses: () => request('/analyses?limit=100'),
  getAnalysis: (id) => request(`/analyses/${id}`),
  deleteAnalysis: (id) => request(`/analyses/${id}`, { method: 'DELETE' }),
}

// The API returns ISO timestamps; SQLite-backed dev servers omit the timezone.
export function formatDate(value) {
  const iso = /[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : `${value}Z`
  return new Date(iso).toLocaleDateString(undefined, { dateStyle: 'medium' })
}

export function formatSize(bytes) {
  return bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
