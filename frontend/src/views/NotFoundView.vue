<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const router = useRouter()
const auth = useAuthStore()

function goHome() {
  if (auth.isAuthenticated) {
    const role = auth.user?.role?.toLowerCase()
    if (role === 'patient') router.push('/patient/accueil')
    else router.push('/dashboard/accueil')
  } else {
    router.push('/')
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center" style="background:#f4f7fb">
    <div class="text-center max-w-md px-6">
      <!-- Illustration -->
      <div class="w-32 h-32 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-6">
        <svg class="w-16 h-16 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>

      <div class="text-8xl font-extrabold text-blue-200 mb-2">404</div>
      <h1 class="text-2xl font-extrabold text-gray-900 mb-2">Page introuvable</h1>
      <p class="text-gray-500 mb-8 leading-relaxed">
        La page que vous recherchez n'existe pas ou a été déplacée.<br>
        Vérifiez l'URL ou retournez à l'accueil.
      </p>

      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <button @click="router.back()"
          class="flex items-center justify-center gap-2 px-6 py-3 rounded-xl border-2 border-blue-200 text-blue-700 font-semibold hover:bg-blue-50 transition-colors">
          ← Retour
        </button>
        <button @click="goHome"
          class="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-700 text-white font-semibold hover:bg-blue-800 transition-colors">
          🏠 Accueil
        </button>
      </div>

      <div class="mt-8 p-4 bg-white rounded-xl border border-gray-100 text-left">
        <p class="text-xs font-bold text-gray-500 mb-2">Liens utiles</p>
        <div class="space-y-1">
          <RouterLink to="/" class="block text-sm text-blue-600 hover:underline">→ Site du DIGNE HOSPITAL</RouterLink>
          <RouterLink to="/login/patient" class="block text-sm text-blue-600 hover:underline">→ Espace Patient</RouterLink>
          <RouterLink to="/login/professionnel" class="block text-sm text-blue-600 hover:underline">→ Espace Professionnel</RouterLink>
        </div>
      </div>

      <p class="text-xs text-gray-400 mt-6">DIGNE HOSPITAL · SGHL v2.0 · support@digne-hospital.gn</p>
    </div>
  </div>
</template>
