<script setup>
import { ref } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useAuthStore } from '@/stores/auth'

const store = useAccountsStore()
const auth  = useAuthStore()
const identifiant  = ref('')
const motdepasse   = ref('')
const erreur       = ref('')
const chargement   = ref(false)
const voirMdp      = ref(false)
const notifVisible = ref(false)
const notifEmail   = ref('')

async function connecter() {
  erreur.value     = ''
  chargement.value = true

  const id  = identifiant.value.trim().toLowerCase()
  const mdp = motdepasse.value

  if (!id || !mdp) {
    erreur.value = 'Veuillez remplir tous les champs.'
    chargement.value = false
    return
  }

  await new Promise(r => setTimeout(r, 600))

  try {
    // Passe par auth store — gère comptes locaux + API réelle + mock auto
    const userData = await auth.login({ username: id, password: mdp })
    notifEmail.value   = userData.email || id
    notifVisible.value = true
    setTimeout(() => window.location.replace('/dashboard/accueil'), 1500)
  } catch (e) {
    erreur.value = e?.message || 'Identifiant ou mot de passe incorrect.'
    chargement.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background:#f4f7fb">
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
      <a href="/" class="text-gray-600 hover:text-blue-700 text-sm font-medium">← Retour au site</a>
      <span class="font-bold text-gray-900 text-sm">🏥 DIGNE HOSPITAL</span>
    </div>

    <!-- Notification connexion -->
    <div v-if="notifVisible"
      class="fixed top-4 right-4 z-50 bg-green-600 text-white rounded-2xl shadow-2xl p-5 max-w-sm border border-green-500 animate-pulse">
      <div class="flex items-start gap-3">
        <span class="text-2xl shrink-0">📧</span>
        <div>
          <p class="font-bold text-sm">Connexion réussie !</p>
          <p class="text-xs text-green-100 mt-1">Un email de notification a été envoyé à :</p>
          <p class="font-mono text-xs text-white font-bold mt-0.5">{{ notifEmail }}</p>
          <p class="text-xs text-green-100 mt-1">Redirection en cours...</p>
        </div>
      </div>
    </div>

    <div class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-lg p-8 border border-blue-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-700 to-violet-600 flex items-center justify-center text-white text-xl shrink-0">🩺</div>
            <div>
              <h2 class="text-2xl font-extrabold text-gray-900">Espace Professionnel</h2>
              <p class="text-gray-500 text-sm">Accès sécurisé au système clinique</p>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Identifiant</label>
              <input v-model="identifiant" type="text" class="input-field" placeholder="prenom.nom"
                autocomplete="username" @keyup.enter="connecter" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Mot de passe</label>
              <div class="relative">
                <input v-model="motdepasse" :type="voirMdp ? 'text' : 'password'"
                  class="input-field pr-10" placeholder="••••••••" @keyup.enter="connecter" />
                <button type="button" @click="voirMdp = !voirMdp"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600 text-sm">
                  {{ voirMdp ? '🙈' : '👁️' }}
                </button>
              </div>
            </div>

            <div v-if="erreur" class="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
              ❌ {{ erreur }}
            </div>

            <button @click="connecter" :disabled="chargement"
              class="w-full py-3 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-bold text-sm transition-all disabled:opacity-60 flex items-center justify-center gap-2">
              <svg v-if="chargement" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ chargement ? 'Connexion en cours...' : '🔐 Se connecter' }}
            </button>
          </div>

          <!-- Créer compte — OBLIGATOIRE -->
          <div class="mt-5 p-4 bg-gradient-to-r from-blue-50 to-violet-50 border border-blue-200 rounded-xl text-center">
            <p class="text-sm font-semibold text-gray-700 mb-1">Pas encore de compte ?</p>
            <p class="text-xs text-gray-500 mb-3">Créez votre compte — vous recevrez un email + SMS de confirmation</p>
            <a href="/register"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold text-sm hover:from-blue-700 hover:to-violet-700 transition-all shadow-sm">
              📝 Créer mon compte professionnel
            </a>
          </div>

          <div class="mt-3 text-center">
            <a href="#" @click.prevent="alert('Contactez l\'administrateur : +224 620 000 000')"
              class="text-xs text-blue-600 hover:underline">Mot de passe oublié ?</a>
          </div>

          <div class="mt-4 flex gap-2">
            <a href="/login/patient" class="flex-1 text-center py-2 rounded-lg bg-blue-50 text-blue-700 text-xs font-semibold hover:bg-blue-100 transition-colors">👤 Espace Patient</a>
            <a href="/login/admin" class="flex-1 text-center py-2 rounded-lg bg-slate-50 text-slate-700 text-xs font-semibold hover:bg-slate-100 transition-colors">⚙️ Administration</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
