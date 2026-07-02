<script setup>
import { ref, reactive } from 'vue'
import { useAccountsStore } from '@/stores/accounts'

const store = useAccountsStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error   = ref('')
const showPwd = ref(false)
const notifVisible = ref(false)
const notifEmail   = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  const id = form.username.toLowerCase().trim()
  const pwd = form.password

  if (!id || !pwd) {
    error.value = 'Veuillez remplir tous les champs.'
    loading.value = false; return
  }

  await new Promise(r => setTimeout(r, 800))

  // 1. Store local
  const acc = store.login(id, pwd)
  if (acc && acc.role === 'Patient') {
    notifEmail.value = acc.email
    notifVisible.value = true
    localStorage.setItem('sghl_token', 'local_' + acc.username + '_' + Date.now())
    localStorage.setItem('sghl_user', JSON.stringify({
      username: acc.username, role: acc.role, full_name: acc.full_name,
      prenom: acc.prenom, nom: acc.nom, nss: 'PAT-' + acc.id,
    }))
    setTimeout(() => window.location.href = '/patient/accueil', 1800)
    return
  }

  // 2. API réelle
  try {
    const res = await fetch('/api/v1/auth/login/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: id, password: pwd })
    })
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('sghl_token', data.access)
      localStorage.setItem('sghl_user', JSON.stringify(data.user || { username: id, role: 'Patient' }))
      window.location.href = '/patient/accueil'; return
    }
  } catch { /* API indisponible */ }

  error.value = 'Identifiant ou mot de passe incorrect. Veuillez d\'abord créer un compte patient.'
  loading.value = false
}
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #e0e7ff 100%)">
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
      <a href="/" class="text-gray-700 hover:text-blue-700 text-sm font-medium flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Retour
      </a>
      <span class="font-bold text-gray-900 text-sm">DIGNE HOSPITAL</span>
    </div>

    <!-- Notification connexion -->
    <div v-if="notifVisible"
      class="fixed top-4 right-4 z-50 bg-green-600 text-white rounded-2xl shadow-2xl p-5 max-w-sm border border-green-500">
      <div class="flex items-start gap-3">
        <span class="text-2xl shrink-0">📧</span>
        <div>
          <p class="font-bold text-sm">Connexion réussie !</p>
          <p class="text-xs text-green-100 mt-1">Notification envoyée à :</p>
          <p class="font-mono text-xs text-white font-bold mt-0.5">{{ notifEmail }}</p>
          <p class="text-xs text-green-100 mt-1">Redirection vers votre espace...</p>
        </div>
      </div>
    </div>

    <div class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-blue-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white text-xl shrink-0">👤</div>
            <div>
              <h2 class="text-2xl font-extrabold text-gray-900">Espace Patient</h2>
              <p class="text-gray-500 text-sm">Accédez à votre dossier médical sécurisé</p>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Identifiant</label>
              <input v-model="form.username" type="text" class="input-field" placeholder="prenom.nom" required />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Mot de passe</label>
              <div class="relative">
                <input v-model="form.password" :type="showPwd ? 'text' : 'password'"
                  class="input-field pr-10" placeholder="••••••••" required />
                <button type="button" @click="showPwd = !showPwd"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">{{ error }}</div>

            <button type="submit" :disabled="loading"
              class="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-60">
              <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ loading ? 'Connexion...' : 'Accéder à mon espace' }}
            </button>
          </form>

          <!-- Créer compte OBLIGATOIRE -->
          <div class="mt-5 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl text-center">
            <p class="text-sm font-semibold text-gray-700 mb-1">Nouveau patient ?</p>
            <p class="text-xs text-gray-500 mb-3">Créez votre compte — email + SMS de confirmation inclus</p>
            <a href="/register"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold text-sm hover:from-blue-700 hover:to-cyan-600 transition-all shadow-sm">
              📝 Créer mon compte patient
            </a>
          </div>

          <div class="mt-3 text-center">
            <a href="#" @click.prevent="alert('Contactez le secrétariat : +224 620 000 010')"
              class="text-xs text-blue-600 hover:underline">Mot de passe oublié ?</a>
          </div>

          <div class="mt-4 flex gap-2">
            <a href="/login/professionnel" class="flex-1 text-center py-2 rounded-lg bg-blue-50 text-blue-700 text-xs font-semibold hover:bg-blue-100 transition-colors">🩺 Espace Pro</a>
            <a href="/login/admin" class="flex-1 text-center py-2 rounded-lg bg-slate-50 text-slate-700 text-xs font-semibold hover:bg-slate-100 transition-colors">⚙️ Administration</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
