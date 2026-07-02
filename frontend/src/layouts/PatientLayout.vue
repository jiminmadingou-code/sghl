<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const mobileMenuOpen = ref(false)

const navItems = [
  { name: 'Accueil',           path: '/patient/accueil',          icon: '🏠' },
  { name: 'Mes rendez-vous',   path: '/patient/rendez-vous',       icon: '📅' },
  { name: 'Mes résultats',     path: '/patient/resultats',         icon: '🔬' },
  { name: 'Imagerie',          path: '/patient/imagerie',          icon: '🫁' },
  { name: 'Mes ordonnances',   path: '/patient/ordonnances',       icon: '💊' },
  { name: 'Mes factures',      path: '/patient/factures',          icon: '💳' },
  { name: 'Messagerie',        path: '/patient/messagerie',        icon: '💬' },
  { name: 'Hospitalisations',  path: '/patient/hospitalisations',  icon: '🏥' },
  { name: 'Admission en ligne',path: '/patient/admission',         icon: '📝' },
  { name: 'Partage dossier',   path: '/patient/partage',           icon: '🔗' },
  { name: 'Livret d\'accueil', path: '/patient/livret',            icon: '📖' },
]

const patient = computed(() => auth.user || { prenom: 'Mamadou', nom: 'Diallo', nss: 'PAT-00001' })
const initials = computed(() => {
  const p = patient.value
  return ((p.prenom?.[0] || '') + (p.nom?.[0] || '')).toUpperCase() || 'P'
})

function logout() {
  localStorage.removeItem('sghl_token')
  localStorage.removeItem('sghl_user')
  window.location.href = '/'
}
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background:#f0f7ff">

    <!-- Top header -->
    <header class="bg-white border-b border-blue-100 shadow-sm sticky top-0 z-40">

      <!-- Urgences band -->
      <div class="bg-red-600 text-white text-xs py-1.5 px-4 flex items-center justify-between">
        <span class="font-semibold flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse inline-block"></span>
          Urgences 24h/24 — 7j/7
        </span>
        <span class="font-bold">📞 +224 620 000 001</span>
      </div>

      <!-- Main header -->
      <div class="px-4 py-3 flex items-center justify-between max-w-7xl mx-auto">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shrink-0">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div class="hidden sm:block">
            <p class="font-extrabold text-gray-900 text-sm leading-tight">DIGNE HOSPITAL</p>
            <p class="text-xs text-blue-600 font-semibold">Mon Espace Patient</p>
          </div>
        </RouterLink>

        <!-- Nav desktop -->
        <nav class="hidden lg:flex items-center gap-1">
          <RouterLink
            v-for="item in navItems" :key="item.path"
            :to="item.path"
            :class="['flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium transition-all',
              route.path === item.path
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700']"
          >
            <span class="text-base">{{ item.icon }}</span>
            <span class="hidden xl:inline">{{ item.name }}</span>
          </RouterLink>
        </nav>

        <!-- User + logout -->
        <div class="flex items-center gap-3">
          <div class="hidden sm:flex items-center gap-2.5 bg-blue-50 border border-blue-100 rounded-xl px-3 py-2">
            <div class="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
              {{ initials }}
            </div>
            <div class="hidden md:block">
              <p class="text-xs font-bold text-gray-900 leading-tight">{{ patient.prenom }} {{ patient.nom }}</p>
              <p class="text-[10px] text-blue-600">{{ patient.nss || 'PAT-00001' }}</p>
            </div>
          </div>
          <button @click="logout" class="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            <span class="hidden sm:inline">Déconnexion</span>
          </button>
          <!-- Burger mobile -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="lg:hidden p-2 rounded-xl hover:bg-gray-100">
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile nav -->
      <div v-if="mobileMenuOpen" class="lg:hidden border-t border-gray-100 bg-white px-4 py-3 grid grid-cols-2 gap-2">
        <RouterLink
          v-for="item in navItems" :key="item.path"
          :to="item.path"
          @click="mobileMenuOpen = false"
          :class="['flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
            route.path === item.path ? 'bg-blue-600 text-white' : 'bg-gray-50 text-gray-700 hover:bg-blue-50']"
        >
          <span>{{ item.icon }}</span> {{ item.name }}
        </RouterLink>
      </div>
    </header>

    <!-- Page content -->
    <main class="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-blue-100 py-4 px-4 text-center text-xs text-gray-400">
      DIGNE HOSPITAL · Mon Espace Patient · Données chiffrées AES-256 · Conforme RGPD
      <span class="mx-2">·</span>
      <RouterLink to="/" class="text-blue-500 hover:underline">Retour au site</RouterLink>
    </footer>
  </div>
</template>
