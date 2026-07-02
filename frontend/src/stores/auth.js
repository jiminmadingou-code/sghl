import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

function notifyLogin(user) {
  const date = new Date().toLocaleString('fr-FR')
  console.log(`\n📧 EMAIL → ${user.email || 'N/A'}\n🔐 Connexion DIGNE HOSPITAL — ${user.full_name} — ${date}`)
  if (user.telephone) console.log(`📱 SMS → ${user.telephone}: Connexion détectée le ${date}.`)
  window.dispatchEvent(new CustomEvent('sghl:login-notif', {
    detail: { email: user.email, telephone: user.telephone, name: user.full_name, date }
  }))
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('sghl_token') || null)
  const user  = ref((() => {
    try { return JSON.parse(localStorage.getItem('sghl_user')) } catch { return null }
  })())

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    const username = (credentials.username || credentials.email || '').toLowerCase().trim()
    const password = credentials.password || ''

    // 1. Comptes créés via RegisterView (localStorage) — confirmés ou mode démo
    try {
      const accounts = JSON.parse(localStorage.getItem('sghl_accounts') || '[]')
      const acc = accounts.find(a =>
        (a.username === username || a.email === username) && a.password === password
      )
      if (acc) {
        // Confirmer automatiquement en mode démo
        acc.confirmed = true
        localStorage.setItem('sghl_accounts', JSON.stringify(accounts))
        const userData = { username: acc.username, full_name: acc.full_name, role: acc.role, service: acc.service || '', email: acc.email, telephone: acc.telephone || '' }
        token.value = 'token_' + Date.now()
        user.value  = userData
        localStorage.setItem('sghl_token', token.value)
        localStorage.setItem('sghl_user',  JSON.stringify(userData))
        notifyLogin(userData)
        return userData
      }
    } catch { /* ignore */ }

    // 2. API (backend réel ou mock automatique — jamais d'erreur réseau)
    try {
      const { default: api } = await import('@/services/api')
      const { data } = await api.post('/auth/login/', { username, password })
      token.value = data.access
      user.value  = data.user || { username, role: 'Médecin', full_name: username, email: '' }
      localStorage.setItem('sghl_token', token.value)
      localStorage.setItem('sghl_user',  JSON.stringify(user.value))
      notifyLogin(user.value)
      return user.value
    } catch (e) {
      throw new Error(e?.response?.data?.detail || 'Identifiants incorrects')
    }
  }

  function logout() {
    token.value = null; user.value = null
    localStorage.removeItem('sghl_token'); localStorage.removeItem('sghl_user')
  }

  return { token, user, isAuthenticated, login, logout }
})
