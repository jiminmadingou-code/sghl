<script setup>
import { ref, reactive, computed } from 'vue'

// Modes : 'login' | 'register' | 'confirm' | 'done'
const mode = ref('login')
const loading = ref(false)
const error = ref('')
const showPwd = ref(false)

// ─── Formulaire login ───
const loginForm = reactive({ email: '', password: '' })

// ─── Formulaire inscription ───
const regForm = reactive({ prenom: '', nom: '', email: '', telephone: '', matricule: '', password: '', confirm: '' })

// ─── Confirmation email ───
const confirmCode = ref('')
const pendingAdmin = ref(null)
const generatedCode = ref('')    // utilisé uniquement en mode démo (backend hors ligne)
const useBackendConfirm = ref(false) // true = le code a été envoyé par SMTP réel

// ─── Helpers localStorage ───
const STORAGE_KEY = 'sghl_accounts'
function loadAccounts() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') } catch { return [] }
}
function saveAccounts(list) { localStorage.setItem(STORAGE_KEY, JSON.stringify(list)) }

// ─── Indicateur force mot de passe ───
const pwdStrength = computed(() => {
  const p = regForm.password
  if (!p) return { score: 0, label: '', color: '' }
  let s = 0
  if (p.length >= 8) s++
  if (/[A-Z]/.test(p)) s++
  if (/[0-9]/.test(p)) s++
  if (/[^A-Za-z0-9]/.test(p)) s++
  return [
    { score: 0, label: '', color: '' },
    { score: 1, label: 'Faible',    color: 'bg-red-500' },
    { score: 2, label: 'Moyen',     color: 'bg-amber-500' },
    { score: 3, label: 'Bon',       color: 'bg-blue-500' },
    { score: 4, label: 'Excellent', color: 'bg-green-500' },
  ][s]
})

// ─── INSCRIPTION ADMIN ───
async function handleRegister() {
  error.value = ''
  if (!regForm.prenom || !regForm.nom || !regForm.email || !regForm.password) {
    error.value = 'Veuillez remplir tous les champs obligatoires.'; return
  }
  if (regForm.password !== regForm.confirm) {
    error.value = 'Les mots de passe ne correspondent pas.'; return
  }
  if (regForm.password.length < 8) {
    error.value = 'Le mot de passe doit contenir au moins 8 caractères.'; return
  }
  loading.value = true

  const accounts = loadAccounts()
  if (accounts.find(a => a.email === regForm.email)) {
    error.value = 'Un compte avec cet email existe déjà.'; loading.value = false; return
  }

  // Appel backend réel d'abord, fallback local si indisponible
  try {
    const res = await fetch('/api/v1/auth/send-confirm-code/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: regForm.email, nom: `${regForm.prenom} ${regForm.nom}` })
    })
    const json = await res.json()
    if (json.status === 'sent') {
      // Email envoyé via SMTP réel
      useBackendConfirm.value = true
    } else {
      // SMTP non configuré — mode démo avec code local
      const code = String(Math.floor(100000 + Math.random() * 900000))
      generatedCode.value = code
      useBackendConfirm.value = false
      console.log(`📧 [DÉMO] Code de confirmation : ${code}`)
    }
  } catch {
    // Backend hors ligne — mode démo pur
    const code = String(Math.floor(100000 + Math.random() * 900000))
    generatedCode.value = code
    useBackendConfirm.value = false
    console.log(`📧 [DÉMO hors-ligne] Code : ${code}`)
  }

  pendingAdmin.value = {
    prenom: regForm.prenom, nom: regForm.nom,
    email: regForm.email, telephone: regForm.telephone,
    matricule: regForm.matricule, password: regForm.password,
  }
  loading.value = false
  mode.value = 'confirm'
}

// ─── CONFIRMATION DU CODE ───
async function handleConfirm() {
  error.value = ''
  if (!confirmCode.value) { error.value = 'Saisissez le code reçu par email.'; return }
  loading.value = true

  // Si backend disponible : vérifier via API
  if (useBackendConfirm.value) {
    try {
      const username = `${pendingAdmin.value.prenom}.${pendingAdmin.value.nom}`.toLowerCase().replace(/\s/g, '.')
      const res = await fetch('/api/v1/auth/verify-confirm-code/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: pendingAdmin.value.email, code: confirmCode.value.trim(),
          username, password: pendingAdmin.value.password,
          prenom: pendingAdmin.value.prenom, nom: pendingAdmin.value.nom,
        })
      })
      const json = await res.json()
      if (!res.ok || json.error) {
        error.value = json.error || 'Code incorrect.'; loading.value = false; return
      }
      // Sauvegarder aussi en local pour login immédiat
      _saveLocalAdmin(username)
      loading.value = false; mode.value = 'done'; return
    } catch {
      // Backend indisponible : basculer en vérif locale
    }
  }

  // Mode démo : vérification locale
  if (confirmCode.value.trim() !== generatedCode.value) {
    error.value = 'Code incorrect. Vérifiez votre email et réessayez.'; loading.value = false; return
  }
  const username = `${pendingAdmin.value.prenom}.${pendingAdmin.value.nom}`.toLowerCase().replace(/\s/g, '.')
  _saveLocalAdmin(username)
  loading.value = false; mode.value = 'done'
}

function _saveLocalAdmin(username) {
  const accounts = loadAccounts()
  if (!accounts.find(a => a.email === pendingAdmin.value.email)) {
    accounts.push({
      id: Date.now(), username,
      email: pendingAdmin.value.email,
      telephone: pendingAdmin.value.telephone || '',
      prenom: pendingAdmin.value.prenom, nom: pendingAdmin.value.nom,
      full_name: `${pendingAdmin.value.prenom} ${pendingAdmin.value.nom}`,
      password: pendingAdmin.value.password,
      role: 'Admin', service: 'Direction',
      matricule: pendingAdmin.value.matricule || '',
      confirmed: true, created_at: new Date().toISOString(),
    })
    saveAccounts(accounts)
  }
  console.log(`✅ Compte admin confirmé : ${pendingAdmin.value.email}`)
}

// ─── CONNEXION ADMIN ───
async function handleLogin() {
  error.value = ''
  loading.value = true
  const id = loginForm.email.toLowerCase().trim()
  const pwd = loginForm.password

  const accounts = loadAccounts()
  const acc = accounts.find(a =>
    (a.email === id || a.username === id) &&
    a.password === pwd &&
    (a.role === 'Admin' || a.role === 'admin') &&
    a.confirmed === true
  )

  if (acc) {
    const userData = { username: acc.username, full_name: acc.full_name, role: 'Admin', service: acc.service || 'Direction', email: acc.email, telephone: acc.telephone || '' }
    localStorage.setItem('sghl_token', 'admin_token_' + Date.now())
    localStorage.setItem('sghl_user', JSON.stringify(userData))

    // Notification connexion
    console.log(`🔐 Connexion admin : ${acc.email} — ${new Date().toLocaleString('fr-FR')}`)
    window.dispatchEvent(new CustomEvent('sghl:login-notif', {
      detail: { email: acc.email, telephone: acc.telephone, name: acc.full_name, date: new Date().toLocaleString('fr-FR') }
    }))

    window.location.href = '/dashboard/accueil'
    return
  }

  // Tentative API backend
  try {
    const res = await fetch('/api/v1/auth/login/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: id, password: pwd })
    })
    if (!res.ok) throw new Error()
    const data = await res.json()
    localStorage.setItem('sghl_token', data.access)
    localStorage.setItem('sghl_user', JSON.stringify(data.user || { username: id, role: 'Admin' }))
    window.location.href = '/dashboard/accueil'
  } catch {
    error.value = 'Identifiants incorrects ou compte non confirmé.'
    loading.value = false
  }
}

// ─── Renvoyer le code ───
async function renvoyerCode() {
  confirmCode.value = ''
  error.value = ''
  if (useBackendConfirm.value) {
    try {
      await fetch('/api/v1/auth/send-confirm-code/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: pendingAdmin.value?.email, nom: pendingAdmin.value?.prenom })
      })
    } catch { /* ignore */ }
  } else {
    const code = String(Math.floor(100000 + Math.random() * 900000))
    generatedCode.value = code
    console.log(`📧 Nouveau code démo : ${code}`)
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-6"
    style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e1b4b 100%)">

    <div class="w-full max-w-md">

      <!-- Logo -->
      <div class="text-center mb-6">
        <div class="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center mx-auto mb-3">
          <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
        </div>
        <h1 class="text-2xl font-extrabold text-white">DIGNE HOSPITAL</h1>
        <p class="text-slate-400 text-sm mt-1">Espace Administrateur</p>
      </div>

      <!-- ── MODE : CONNEXION ── -->
      <div v-if="mode === 'login'" class="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8">
        <h2 class="text-white font-bold text-lg mb-5">Se connecter</h2>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-300 mb-1.5">Email ou identifiant</label>
            <input v-model="loginForm.email" type="text"
              class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400 transition-all"
              placeholder="prenom.nom ou email@sghl.cg" required />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-300 mb-1.5">Mot de passe</label>
            <div class="relative">
              <input v-model="loginForm.password" :type="showPwd ? 'text' : 'password'"
                class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400 transition-all pr-10"
                placeholder="••••••••" required />
              <button type="button" @click="showPwd = !showPwd"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white text-sm">
                {{ showPwd ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <div v-if="error" class="bg-red-900/30 border border-red-500/30 text-red-300 text-sm rounded-xl px-4 py-3">
            ❌ {{ error }}
          </div>

          <button type="submit" :disabled="loading"
            class="w-full py-3 rounded-xl bg-slate-600 hover:bg-slate-500 text-white font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-60">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? 'Connexion...' : '🔐 Accéder au panneau admin' }}
          </button>
        </form>

        <div class="mt-5 pt-4 border-t border-white/10 text-center">
          <p class="text-gray-400 text-sm">Pas encore de compte administrateur ?</p>
          <button @click="mode = 'register'; error = ''"
            class="mt-2 text-blue-400 hover:text-blue-300 font-semibold text-sm underline underline-offset-2">
            ➕ Créer un compte admin
          </button>
        </div>

        <div class="mt-4 flex gap-2">
          <a href="/login/patient" class="flex-1 text-center py-2 rounded-xl bg-white/8 text-gray-400 text-xs font-medium hover:bg-white/15 transition-colors">👤 Espace Patient</a>
          <a href="/login/professionnel" class="flex-1 text-center py-2 rounded-xl bg-white/8 text-gray-400 text-xs font-medium hover:bg-white/15 transition-colors">🩺 Espace Pro</a>
        </div>
      </div>

      <!-- ── MODE : INSCRIPTION ── -->
      <div v-else-if="mode === 'register'" class="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8">
        <div class="flex items-center gap-3 mb-5">
          <button @click="mode = 'login'; error = ''" class="text-gray-400 hover:text-white text-xl">←</button>
          <h2 class="text-white font-bold text-lg">Créer un compte Administrateur</h2>
        </div>

        <div class="bg-blue-900/30 border border-blue-500/30 rounded-xl p-3 mb-5 text-xs text-blue-300">
          📧 Un code de confirmation sera envoyé à votre adresse email. Vous devrez le saisir pour activer votre compte.
        </div>

        <form @submit.prevent="handleRegister" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1">Prénom *</label>
              <input v-model="regForm.prenom" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400" placeholder="Moussa" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1">Nom *</label>
              <input v-model="regForm.nom" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400" placeholder="Traoré" required />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Adresse email * <span class="text-blue-400">(recevra le code de confirmation)</span></label>
            <input v-model="regForm.email" type="email" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400" placeholder="admin@digne-hospital.cg" required />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Téléphone</label>
            <input v-model="regForm.telephone" type="tel" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400" placeholder="+242 06 000 0000" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">N° Matricule</label>
            <input v-model="regForm.matricule" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400" placeholder="MAT-ADMIN-001" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Mot de passe * <span class="text-gray-500">(min. 8 caractères)</span></label>
            <div class="relative">
              <input v-model="regForm.password" :type="showPwd ? 'text' : 'password'"
                class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400 pr-9"
                placeholder="••••••••" required />
              <button type="button" @click="showPwd = !showPwd" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white text-xs">{{ showPwd ? '🙈' : '👁️' }}</button>
            </div>
            <div v-if="regForm.password" class="mt-1.5 flex gap-1">
              <div v-for="i in 4" :key="i" :class="['h-1 flex-1 rounded-full transition-colors', i <= pwdStrength.score ? pwdStrength.color : 'bg-white/20']"/>
            </div>
            <p v-if="regForm.password" class="text-xs mt-0.5" :class="pwdStrength.score >= 3 ? 'text-green-400' : 'text-amber-400'">
              Force : {{ pwdStrength.label }}
            </p>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-300 mb-1">Confirmer le mot de passe *</label>
            <input v-model="regForm.confirm" type="password" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-2 text-white text-sm placeholder-gray-500 outline-none focus:border-slate-400" placeholder="••••••••" required />
            <p v-if="regForm.confirm && regForm.password !== regForm.confirm" class="text-xs text-red-400 mt-0.5">⚠ Les mots de passe ne correspondent pas</p>
          </div>

          <div v-if="error" class="bg-red-900/30 border border-red-500/30 text-red-300 text-sm rounded-xl px-4 py-3">❌ {{ error }}</div>

          <button type="submit" :disabled="loading"
            class="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-60 mt-2">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? 'Envoi du code...' : '📧 Envoyer le code de confirmation' }}
          </button>
        </form>
      </div>

      <!-- ── MODE : CONFIRMATION EMAIL ── -->
      <div v-else-if="mode === 'confirm'" class="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8 text-center">
        <div class="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-4 text-3xl">📧</div>
        <h2 class="text-white font-bold text-lg mb-1">Confirmez votre email</h2>
        <p class="text-gray-400 text-sm mb-1">Un code à 6 chiffres a été envoyé à :</p>
        <p class="text-blue-400 font-bold mb-5">{{ pendingAdmin?.email }}</p>

        <!-- Mode démo uniquement si SMTP non configuré -->
        <div v-if="!useBackendConfirm" class="bg-amber-900/30 border border-amber-500/30 rounded-xl p-3 mb-5 text-left">
          <p class="text-xs text-amber-300 font-bold mb-1">🧪 Mode démo — backend hors ligne. Code visible ici :</p>
          <p class="text-amber-200 font-mono text-xl text-center tracking-[0.3em] font-bold">{{ generatedCode }}</p>
          <p class="text-xs text-amber-400 mt-1 text-center">Démarrez le backend pour recevoir le vrai email</p>
        </div>
        <!-- Confirmation SMTP réel -->
        <div v-else class="bg-green-900/30 border border-green-500/30 rounded-xl p-3 mb-5">
          <p class="text-xs text-green-300">✅ Un email a été envoyé à <strong>{{ pendingAdmin?.email }}</strong></p>
          <p class="text-xs text-green-400 mt-1">Vérifiez votre boîte de réception (et les spams).</p>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-semibold text-gray-300 mb-2 text-left">Code de confirmation *</label>
          <input v-model="confirmCode"
            class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white text-xl text-center font-mono tracking-[0.3em] placeholder-gray-600 outline-none focus:border-blue-400 transition-all"
            placeholder="000000" maxlength="6" />
        </div>

        <div v-if="error" class="bg-red-900/30 border border-red-500/30 text-red-300 text-sm rounded-xl px-4 py-3 mb-4">❌ {{ error }}</div>

        <button @click="handleConfirm" :disabled="loading"
          class="w-full py-3 rounded-xl bg-green-600 hover:bg-green-500 text-white font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-60 mb-3">
          <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          {{ loading ? 'Vérification...' : '✅ Confirmer mon compte' }}
        </button>

        <button @click="renvoyerCode" class="text-xs text-gray-400 hover:text-white underline transition-colors">
          📨 Renvoyer le code
        </button>
      </div>

      <!-- ── MODE : SUCCÈS ── -->
      <div v-else-if="mode === 'done'" class="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8 text-center">
        <div class="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4 text-3xl">✅</div>
        <h2 class="text-white font-bold text-xl mb-2">Compte créé et confirmé !</h2>
        <p class="text-gray-400 text-sm mb-5">Votre compte administrateur est actif. Vous pouvez maintenant vous connecter.</p>
        <button @click="mode = 'login'; error = ''"
          class="w-full py-3 rounded-xl bg-slate-600 hover:bg-slate-500 text-white font-bold text-sm transition-all">
          🔐 Se connecter maintenant
        </button>
      </div>

    </div>

    <p class="text-center text-xs text-gray-600 mt-4">
      <a href="/" class="hover:text-gray-400 transition-colors">← Retour au site</a>
    </p>
  </div>
</template>
