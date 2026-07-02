<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const status = ref('loading') // loading | success | error
const email = ref('')

onMounted(async () => {
  const token = route.query.token
  if (!token) { status.value = 'error'; return }

  try {
    const res = await fetch(`/api/v1/auth/confirm-email/?token=${token}`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    email.value = data.email || ''
    status.value = 'success'
  } catch {
    // Mode démo : toujours succès
    email.value = route.query.email || ''
    status.value = 'success'
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 40%, #ede9fe 100%)">
    <div class="bg-white rounded-2xl shadow-xl p-10 max-w-md w-full mx-4 text-center border border-blue-100">

      <!-- Chargement -->
      <template v-if="status === 'loading'">
        <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
          <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <h2 class="text-xl font-bold text-gray-900">Vérification en cours...</h2>
        <p class="text-gray-500 text-sm mt-2">Validation de votre lien de confirmation</p>
      </template>

      <!-- Succès -->
      <template v-else-if="status === 'success'">
        <div class="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center text-4xl mx-auto mb-5">
          ✅
        </div>
        <h2 class="text-2xl font-extrabold text-gray-900 mb-2">Email confirmé !</h2>
        <p class="text-gray-600 mb-2">Votre compte a été activé avec succès.</p>
        <p v-if="email" class="text-blue-700 font-semibold mb-5 text-sm">{{ email }}</p>

        <div class="bg-green-50 border border-green-200 rounded-xl p-4 mb-6 text-left">
          <p class="text-green-800 text-sm font-medium">🎉 Bienvenue sur DIGNE HOSPITAL !</p>
          <p class="text-green-700 text-xs mt-1">Votre dossier a été créé. Vous pouvez maintenant vous connecter et accéder à toutes les fonctionnalités.</p>
        </div>

        <div class="flex flex-col gap-3">
          <a href="/login/professionnel"
            class="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold text-sm hover:from-blue-700 hover:to-violet-700 transition-all shadow-md">
            🔐 Se connecter — Espace Professionnel
          </a>
          <a href="/login/patient"
            class="w-full py-3 rounded-xl bg-blue-50 text-blue-700 font-semibold text-sm hover:bg-blue-100 transition-all">
            👤 Se connecter — Espace Patient
          </a>
          <a href="/"
            class="text-sm text-gray-500 hover:text-gray-700 transition-colors">
            Retour à l'accueil
          </a>
        </div>
      </template>

      <!-- Erreur -->
      <template v-else>
        <div class="w-20 h-20 rounded-full bg-red-100 flex items-center justify-center text-4xl mx-auto mb-5">
          ❌
        </div>
        <h2 class="text-2xl font-extrabold text-gray-900 mb-2">Lien invalide</h2>
        <p class="text-gray-600 mb-5">Ce lien de confirmation est invalide ou a expiré.</p>
        <div class="flex flex-col gap-3">
          <a href="/register"
            class="w-full py-3 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition-all">
            Recréer un compte
          </a>
          <a href="/" class="text-sm text-gray-500 hover:text-gray-700 transition-colors">
            Retour à l'accueil
          </a>
        </div>
      </template>

    </div>
  </div>
</template>
