<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const form = reactive({ username: '', password: '' })

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form)
    router.push('/dashboard/accueil')
  } catch {
    error.value = 'Identifiants incorrects. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex" style="background: linear-gradient(135deg, #0a1628 0%, #0f2044 40%, #1e3a8a 80%, #1d4ed8 100%)">

    <!-- Left panel -->
    <div class="hidden lg:flex flex-col justify-center px-16 w-1/2 text-white">
      <div class="mb-8">
        <div class="w-14 h-14 rounded-xl bg-white/15 border border-white/20 flex items-center justify-center mb-6">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
        </div>
        <h1 class="text-4xl font-extrabold mb-2">DIGNE HOSPITAL</h1>
        <p class="text-blue-200 text-lg">Système de Gestion Hospitalière<br>et de Laboratoire — SGHL</p>
      </div>
      <div class="space-y-3">
        <div v-for="feat in ['Dossiers patients sécurisés', 'Laboratoire intégré (LIS)', 'Facturation automatisée', 'Tableau de bord temps réel']"
          :key="feat" class="flex items-center gap-3 text-blue-200">
          <div class="w-5 h-5 rounded-full bg-blue-500/40 flex items-center justify-center text-xs">✓</div>
          <span class="text-sm">{{ feat }}</span>
        </div>
      </div>
    </div>

    <!-- Right panel -->
    <div class="flex-1 flex items-center justify-center p-8">
      <div class="bg-white rounded-2xl shadow-2xl p-10 w-full max-w-md">
        <div class="text-center mb-8">
          <div class="w-12 h-12 rounded-xl bg-blue-700 flex items-center justify-center mx-auto mb-4">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <h2 class="text-2xl font-extrabold text-gray-900">Connexion</h2>
          <p class="text-gray-500 text-sm mt-1">Accédez à votre espace SGHL</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Identifiant ou Email</label>
            <input v-model="form.username" type="text" class="input-field" placeholder="nom.prenom ou email@sghl.gn" required />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Mot de passe</label>
            <div class="relative">
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="input-field pr-10" placeholder="••••••••" required />
              <button type="button" @click="showPassword = !showPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
            {{ error }}
          </div>

          <button type="submit" class="btn-primary w-full py-3 text-base justify-center" :disabled="loading">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </form>

        <p class="text-center text-xs text-gray-400 mt-6">
          Accès réservé au personnel autorisé · SGHL v2.0
        </p>
        <p class="text-center text-sm text-gray-500 mt-3">
          Pas encore de compte ?
          <RouterLink to="/register" class="text-blue-600 font-semibold hover:underline">Créer un compte</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
