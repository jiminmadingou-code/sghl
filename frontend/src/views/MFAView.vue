<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const code = ref('')
const loading = ref(false)
const attempts = ref(0)
const method = ref('app') // 'app' | 'sms'

// En mode démo, n'importe quel code à 6 chiffres fonctionne
async function verifier() {
  if (code.value.length !== 6) {
    toast.warning('Le code doit contenir exactement 6 chiffres')
    return
  }
  loading.value = true
  attempts.value++

  await new Promise(r => setTimeout(r, 800)) // simulation

  // Mode démo : code 123456 ou tout code valide
  if (code.value === '123456' || /^\d{6}$/.test(code.value)) {
    toast.success('Authentification MFA réussie ✓')
    const role = auth.user?.role?.toLowerCase()
    if (role === 'patient') router.push('/patient/accueil')
    else router.push('/dashboard/accueil')
  } else {
    toast.error(`Code incorrect (tentative ${attempts.value}/3)`)
    if (attempts.value >= 3) {
      toast.error('Trop de tentatives. Reconnectez-vous.')
      auth.logout()
      router.push('/')
    }
  }
  loading.value = false
}

function renvoyerCode() {
  toast.success('Code renvoyé par SMS au +224 6XX XXX XXX')
  code.value = ''
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center" style="background:#f4f7fb">
    <div class="w-full max-w-md px-6">

      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-xl border border-blue-100 p-8">

        <!-- Header -->
        <div class="text-center mb-7">
          <div class="w-16 h-16 rounded-2xl bg-blue-700 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-extrabold text-gray-900">Vérification MFA</h1>
          <p class="text-gray-500 text-sm mt-1">Authentification à deux facteurs</p>
        </div>

        <!-- Méthode -->
        <div class="flex bg-gray-100 rounded-xl p-1 mb-6">
          <button @click="method = 'app'"
            :class="['flex-1 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5',
              method === 'app' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500']">
            📱 Application
          </button>
          <button @click="method = 'sms'"
            :class="['flex-1 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5',
              method === 'sms' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500']">
            💬 SMS
          </button>
        </div>

        <!-- Instructions -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-5 flex items-start gap-3">
          <span class="text-xl shrink-0">{{ method === 'app' ? '📱' : '💬' }}</span>
          <p class="text-sm text-blue-800">
            <span v-if="method === 'app'">Ouvrez votre application d'authentification (Google Authenticator, Authy) et entrez le code à 6 chiffres affiché.</span>
            <span v-else>Un code à 6 chiffres a été envoyé par SMS au numéro associé à votre compte.</span>
          </p>
        </div>

        <!-- Saisie code -->
        <div class="mb-5">
          <label class="block text-sm font-semibold text-gray-700 mb-2 text-center">Code de vérification</label>
          <input
            v-model="code"
            type="text"
            maxlength="6"
            inputmode="numeric"
            pattern="[0-9]*"
            placeholder="• • • • • •"
            class="w-full text-center text-3xl font-mono font-bold tracking-[0.6em] border-2 border-blue-200 rounded-xl py-4 outline-none focus:border-blue-600 focus:ring-3 focus:ring-blue-100 transition-all bg-gray-50"
            @keyup.enter="verifier"
          />
          <p class="text-center text-xs text-gray-400 mt-2">
            {{ 6 - code.length }} chiffre(s) restant(s)
          </p>
        </div>

        <!-- Tentatives -->
        <div v-if="attempts > 0" class="flex justify-center gap-1.5 mb-4">
          <div v-for="i in 3" :key="i"
            :class="['w-2.5 h-2.5 rounded-full', i <= attempts ? 'bg-red-400' : 'bg-gray-200']">
          </div>
        </div>

        <!-- Bouton vérifier -->
        <button @click="verifier" :disabled="code.length !== 6 || loading"
          class="w-full py-3 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mb-3">
          <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          {{ loading ? 'Vérification...' : 'Vérifier le code' }}
        </button>

        <div class="flex items-center justify-between text-xs">
          <button @click="renvoyerCode" class="text-blue-600 hover:underline font-medium">
            Renvoyer le code
          </button>
          <RouterLink to="/" class="text-gray-400 hover:text-gray-600">
            Annuler
          </RouterLink>
        </div>

        <!-- Mode démo -->
        <div class="mt-5 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-xs font-bold text-green-800 mb-1">🧪 Mode démo</p>
          <p class="text-xs text-green-700">Entrez n'importe quel code à 6 chiffres (ex: <strong>123456</strong>)</p>
          <button @click="code = '123456'" class="mt-1.5 text-xs font-mono font-bold text-green-800 bg-white border border-green-200 px-3 py-1 rounded-lg hover:bg-green-100 transition-colors">
            Remplir : 123456
          </button>
        </div>
      </div>

      <p class="text-center text-xs text-gray-400 mt-4">
        🔒 Connexion chiffrée TLS 1.3 · DIGNE HOSPITAL SGHL v2.0
      </p>
    </div>
  </div>
</template>
