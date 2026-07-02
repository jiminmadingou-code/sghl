<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useI18nStore } from '@/stores/i18n'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const theme = useThemeStore()
const i18n = useI18nStore()
const sidebarOpen = ref(true)
const showNotifPanel = ref(false)
const currentTime = ref(new Date())

let clockInterval = null
onMounted(() => { clockInterval = setInterval(() => { currentTime.value = new Date() }, 1000) })
onUnmounted(() => clearInterval(clockInterval))

const timeStr = computed(() => currentTime.value.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }))
const dateStr = computed(() => currentTime.value.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' }))

const alertesCritiques = ref([
  { id: 1, type: 'danger',  msg: 'Rupture stock : Amoxicilline 500mg',        time: '09:42' },
  { id: 2, type: 'warning', msg: 'Examen urgent en attente : NFS — Diallo M.', time: '10:05' },
  { id: 3, type: 'info',    msg: 'Résultats validés disponibles : Koné F.',    time: '10:18' },
])

const notifications = ref([
  { id: 1, icon: '🔬', title: 'Résultat validé',      desc: 'NFS — Diallo Mamadou',          time: 'Il y a 5 min',  lu: false },
  { id: 2, icon: '💊', title: 'Alerte stock',          desc: 'Amoxicilline < seuil critique', time: 'Il y a 18 min', lu: false },
  { id: 3, icon: '🏥', title: 'Nouvelle admission',    desc: 'Bah Aissatou — Maternité',      time: 'Il y a 32 min', lu: true },
  { id: 4, icon: '📋', title: 'Consultation terminée', desc: 'Dr. Camara — Traoré I.',        time: 'Il y a 1h',     lu: true },
])

const unreadCount = computed(() => notifications.value.filter(n => !n.lu).length)

const navGroups = [
  {
    label: 'Clinique',
    items: [
      { name: 'Tableau de bord',  path: '/dashboard/accueil',         icon: '📊', badge: null },
      { name: 'Patients',         path: '/dashboard/patients',         icon: '👥', badge: null },
      { name: 'Consultations',    path: '/dashboard/consultations',    icon: '🩺', badge: 3 },
      { name: 'Hospitalisations', path: '/dashboard/hospitalisations', icon: '🏥', badge: null },
      { name: 'Soins infirmiers', path: '/dashboard/soins',            icon: '💉', badge: 2 },
      { name: 'Urgences',         path: '/dashboard/urgences',         icon: '🚨', badge: 4 },
      { name: 'Bloc opératoire',  path: '/dashboard/bloc-operatoire',  icon: '🔪', badge: null },
      { name: 'Maternité',        path: '/dashboard/maternite',        icon: '🤱', badge: null },
      { name: 'Téléconsultation', path: '/dashboard/teleconsultation', icon: '📹', badge: null },
    ]
  },
  {
    label: 'Laboratoire & Imagerie',
    items: [
      { name: 'Laboratoire', path: '/dashboard/laboratoire', icon: '🔬', badge: 5 },
      { name: 'Imagerie',    path: '/dashboard/imagerie',    icon: '🩻', badge: null },
      { name: 'Pharmacie',   path: '/dashboard/pharmacie',   icon: '💊', badge: null },
    ]
  },
  {
    label: 'Administration',
    items: [
      { name: 'Facturation', path: '/dashboard/facturation', icon: '💳', badge: null },
      { name: 'Personnel',   path: '/dashboard/personnel',   icon: '👨⚕️', badge: null },
      { name: 'Planning',    path: '/dashboard/planning',    icon: '📅', badge: null },
      { name: 'Rapports',    path: '/dashboard/rapports',    icon: '📈', badge: null },
      { name: 'Paramètres',  path: '/dashboard/parametres',  icon: '⚙️', badge: null },
    ]
  }
]

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return 'AD'
  return ((u.first_name?.[0] || '') + (u.last_name?.[0] || '')).toUpperCase() || 'AD'
})

function logout() {
  localStorage.removeItem('sghl_token')
  localStorage.removeItem('sghl_user')
  window.location.href = '/'
}
function markAllRead() { notifications.value.forEach(n => n.lu = true) }
</script>

<template>
  <div class="flex h-screen overflow-hidden" style="background:#f4f7fb">

    <!-- Sidebar — bleu marine CHU -->
    <aside
      class="sidebar-gradient flex flex-col scrollbar-thin overflow-y-auto transition-all duration-300 shrink-0 z-30"
      :style="{ width: sidebarOpen ? '260px' : '68px' }"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 py-4 border-b border-white/10">
        <div class="w-9 h-9 rounded-lg bg-white/20 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
        </div>
        <transition name="fade">
          <div v-if="sidebarOpen" class="flex-1 min-w-0">
            <p class="text-white font-bold text-sm leading-tight">DIGNE HOSPITAL</p>
            <p class="text-blue-300 text-xs truncate">Espace Professionnel</p>
          </div>
        </transition>
        <button @click="sidebarOpen = !sidebarOpen" class="text-blue-300 hover:text-white transition-colors shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>

      <!-- Status -->
      <div v-if="sidebarOpen" class="mx-3 mt-3 mb-1 px-3 py-2 rounded-lg bg-green-500/15 border border-green-400/20 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-green-400 pulse-dot shrink-0"></span>
        <span class="text-green-300 text-xs font-medium">Système opérationnel</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-2 py-3 space-y-4">
        <div v-for="group in navGroups" :key="group.label">
          <p v-if="sidebarOpen" class="text-blue-400/60 text-[10px] font-bold uppercase tracking-widest px-2 mb-1.5">{{ group.label }}</p>
          <div class="space-y-0.5">
            <RouterLink
              v-for="item in group.items"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: route.path === item.path }"
              :title="!sidebarOpen ? item.name : ''"
            >
              <span class="text-base shrink-0">{{ item.icon }}</span>
              <span v-if="sidebarOpen" class="truncate flex-1">{{ item.name }}</span>
              <span v-if="sidebarOpen && item.badge"
                class="ml-auto bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
                {{ item.badge }}
              </span>
            </RouterLink>
          </div>
        </div>
      </nav>

      <!-- User -->
      <div class="px-3 py-3 border-t border-white/10">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0 ring-2 ring-white/20">
            {{ userInitials }}
          </div>
          <div v-if="sidebarOpen" class="flex-1 min-w-0">
            <p class="text-white text-sm font-semibold truncate">{{ auth.user?.full_name || 'Administrateur' }}</p>
            <p class="text-blue-300 text-xs truncate">{{ auth.user?.role || 'Admin' }}</p>
          </div>
          <button v-if="sidebarOpen" @click="logout" class="text-blue-300 hover:text-red-300 transition-colors" title="Déconnexion">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col overflow-hidden" :style="{ background: 'var(--bg-app)' }">

      <!-- Topbar -->
      <header class="border-b px-6 py-3 flex items-center justify-between shrink-0 shadow-sm"
        :style="{ background: 'var(--bg-topbar)', borderColor: 'var(--border-card)' }">
        <div>
          <h1 class="page-title text-base leading-tight">{{ route.meta.title || route.name }}</h1>
          <p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ dateStr }}</p>
        </div>

        <div class="flex items-center gap-2">
          <!-- Clock -->
          <div class="hidden sm:flex items-center gap-1.5 bg-blue-50 px-3 py-1.5 rounded-lg">
            <svg class="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span class="text-xs font-bold text-blue-700 tabular-nums">{{ timeStr }}</span>
          </div>

          <!-- Alertes -->
          <div v-if="alertesCritiques.length" class="hidden md:flex items-center gap-1.5 bg-red-50 border border-red-200 px-3 py-1.5 rounded-lg">
            <span class="w-2 h-2 rounded-full bg-red-500 pulse-dot"></span>
            <span class="text-xs font-semibold text-red-700">{{ alertesCritiques.length }} alerte(s)</span>
          </div>

          <!-- Toggle Dark Mode -->
          <button @click="theme.toggle()"
            class="p-2 rounded-lg transition-all hover:scale-110"
            :class="theme.isDark ? 'bg-yellow-100 text-yellow-600' : 'bg-gray-100 text-gray-600'"
            :title="theme.isDark ? 'Mode clair' : 'Mode sombre'">
            <span class="text-base">{{ theme.isDark ? '☀️' : '🌙' }}</span>
          </button>

          <!-- Toggle Langue -->
          <button @click="i18n.toggleLang()"
            class="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-bold transition-all"
            :class="theme.isDark ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            :title="i18n.currentLang === 'fr' ? 'Switch to English' : 'Passer en Français'">
            <span>{{ i18n.currentLang === 'fr' ? '🇫🇷' : '🇬🇧' }}</span>
            <span class="hidden sm:inline">{{ i18n.currentLang === 'fr' ? 'FR' : 'EN' }}</span>
          </button>

          <!-- Notifications -->
          <div class="relative">
            <button @click="showNotifPanel = !showNotifPanel"
              class="relative p-2 rounded-lg hover:bg-blue-50 transition-colors">
              <svg class="w-5 h-5 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <span v-if="unreadCount" class="notif-badge">{{ unreadCount }}</span>
            </button>

            <transition name="slide-up">
              <div v-if="showNotifPanel"
                class="absolute right-0 top-11 w-80 rounded-xl shadow-xl border z-50 overflow-hidden"
                :style="{ background: 'var(--bg-card)', borderColor: 'var(--border-card)' }">
                <div class="flex items-center justify-between px-4 py-3 border-b" :style="{ borderColor: 'var(--border-card)' }">
                  <p class="font-bold text-sm" :style="{ color: 'var(--text-primary)' }">{{ i18n.t.common?.info || 'Notifications' }}</p>
                  <button @click="markAllRead" class="text-xs text-blue-600 font-medium hover:underline">Tout marquer lu</button>
                </div>
                <div class="max-h-72 overflow-y-auto">
                  <div v-for="n in notifications" :key="n.id"
                    :class="['flex items-start gap-3 px-4 py-3 border-b hover:bg-blue-50/40 transition-colors',
                      !n.lu ? 'bg-blue-50/20' : '']">
                    <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center text-sm shrink-0">{{ n.icon }}</div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-semibold" :style="{ color: 'var(--text-primary)' }">{{ n.title }}</p>
                      <p class="text-xs truncate" :style="{ color: 'var(--text-muted)' }">{{ n.desc }}</p>
                      <p class="text-xs mt-0.5" :style="{ color: 'var(--text-muted)' }">{{ n.time }}</p>
                    </div>
                    <div v-if="!n.lu" class="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0"></div>
                  </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- Avatar -->
          <div class="w-8 h-8 rounded-full bg-blue-700 flex items-center justify-center text-white text-sm font-bold ring-2 ring-blue-200">
            {{ userInitials }}
          </div>
        </div>
      </header>

      <!-- Alertes banner -->
      <div v-if="alertesCritiques.length" class="bg-red-50 border-b border-red-100 px-6 py-2 flex items-center gap-3 overflow-x-auto shrink-0">
        <span class="text-red-700 font-bold text-xs shrink-0">🚨 ALERTES :</span>
        <div class="flex gap-2">
          <span v-for="a in alertesCritiques" :key="a.id"
            :class="['text-xs font-medium px-3 py-1 rounded-full shrink-0',
              a.type === 'danger'  ? 'bg-red-100 text-red-800' :
              a.type === 'warning' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800']">
            {{ a.msg }}
          </span>
        </div>
      </div>

      <!-- Page -->
      <main class="flex-1 overflow-y-auto p-6">
        <RouterView />
      </main>
    </div>

    <div v-if="showNotifPanel" class="fixed inset-0 z-40" @click="showNotifPanel = false"></div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active { transition: all 0.2s cubic-bezier(0.4,0,0.2,1); }
.slide-up-enter-from { opacity: 0; transform: translateY(-8px); }
</style>
