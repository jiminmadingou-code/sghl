import axios from 'axios'
import { mockResolve } from './mockApi'

// Détecte si le backend est disponible (test au démarrage)
let backendAvailable = null  // null = pas encore testé, true/false = résultat

async function checkBackend() {
  if (backendAvailable !== null) return backendAvailable
  try {
    await axios.get('/api/v1/sante/', { timeout: 2000 })
    backendAvailable = true
  } catch {
    backendAvailable = false
    console.info('[SGHL] Backend non disponible — mode données démo activé.')
  }
  return backendAvailable
}

// Lance le test au chargement (sans bloquer) — échec silencieux garanti
checkBackend().catch(() => { backendAvailable = false })

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 5000,
})

// Injecte le token JWT
axiosInstance.interceptors.request.use(config => {
  const token = localStorage.getItem('sghl_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Intercepteur de réponse : si erreur réseau → mock
axiosInstance.interceptors.response.use(
  res => res,
  async err => {
    const isNetworkError = !err.response || err.code === 'ERR_NETWORK' || err.code === 'ECONNREFUSED'
    if (isNetworkError) {
      backendAvailable = false
      const config = err.config
      const method = config.method?.toUpperCase() || 'GET'
      const url    = config.url || ''
      let body = null
      try { body = config.data ? JSON.parse(config.data) : null } catch {}
      return mockResolve(method, url, body, config.params)
    }
    return Promise.reject(err)
  }
)

// Wrapper principal qui essaie le vrai backend puis bascule sur mock
const api = {
  async get(url, config = {}) {
    const available = await checkBackend()
    if (!available) return mockResolve('GET', url, null, config.params)
    try {
      return await axiosInstance.get(url, config)
    } catch (e) {
      if (!e.response) return mockResolve('GET', url, null, config.params)
      throw e
    }
  },
  async post(url, data, config = {}) {
    const available = await checkBackend()
    if (!available) return mockResolve('POST', url, data, config.params)
    try {
      return await axiosInstance.post(url, data, config)
    } catch (e) {
      if (!e.response) return mockResolve('POST', url, data, config.params)
      throw e
    }
  },
  async put(url, data, config = {}) {
    const available = await checkBackend()
    if (!available) return mockResolve('PUT', url, data, config.params)
    try {
      return await axiosInstance.put(url, data, config)
    } catch (e) {
      if (!e.response) return mockResolve('PUT', url, data, config.params)
      throw e
    }
  },
  async patch(url, data, config = {}) {
    const available = await checkBackend()
    if (!available) return mockResolve('PATCH', url, data, config.params)
    try {
      return await axiosInstance.patch(url, data, config)
    } catch (e) {
      if (!e.response) return mockResolve('PATCH', url, data, config.params)
      throw e
    }
  },
  async delete(url, config = {}) {
    const available = await checkBackend()
    if (!available) return mockResolve('DELETE', url, null, config.params)
    try {
      return await axiosInstance.delete(url, config)
    } catch (e) {
      if (!e.response) return mockResolve('DELETE', url, null, config.params)
      throw e
    }
  },
}

export default api
