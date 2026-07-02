<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18nStore } from '@/stores/i18n'

const i18n = useI18nStore()
const query = ref('')
const isOpen = ref(false)
const isSearching = ref(false)

const searchResults = ref([
  { id: 1, type: 'patient', label: 'Diallo Mamadou', sublabel: 'PAT-00001 · Médecine Interne', icon: '👤', path: '/dashboard/patients/1' },
  { id: 2, type: 'patient', label: 'Koné Fatoumata', sublabel: 'PAT-00002 · Cardiologie', icon: '👤', path: '/dashboard/patients/2' },
  { id: 3, type: 'doctor', label: 'Dr. Camara Alpha', sublabel: 'Médecine Interne · Bâtiment A', icon: '🩺', path: '/dashboard/personnel' },
  { id: 4, type: 'lab', label: 'NFS — Diallo Mamadou', sublabel: 'Résultat disponible · 10/06/2025', icon: '🔬', path: '/patient/resultats' },
  { id: 5, type: 'appointment', label: 'Rendez-vous Dr. Diallo', sublabel: '18/06/2025 · 09:30 · Médecine Interne', icon: '📅', path: '/patient/rendez-vous' },
  { id: 6, type: 'imaging', label: 'Radio Thorax — Koné F.', sublabel: 'Compte-rendu disponible · 08/06/2025', icon: '🩻', path: '/patient/imagerie' },
])

const filteredResults = computed(() => {
  if (!query.value.trim()) return []
  const q = query.value.toLowerCase()
  return searchResults.value.filter(r =>
    r.label.toLowerCase().includes(q) ||
    r.sublabel.toLowerCase().includes(q)
  )
})

const recentSearches = ref([
  { label: 'Diallo Mamadou', icon: '👤', time: 'Il y a 2h' },
  { label: 'NFS résultats', icon: '🔬', time: 'Il y a 1j' },
  { label: 'Dr. Camara', icon: '🩺', time: 'Il y a 3j' },
])

function handleKeydown(e) {
  if (e.key === '/' && !e.target.closest('input, textarea')) {
    e.preventDefault()
    isOpen.value = true
    setTimeout(() => document.getElementById('global-search-input')?.focus(), 100)
  }
  if (e.key === 'Escape') isOpen.value = false
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <!-- Bouton de recherche -->
  <button @click="isOpen = true"
    class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/10 border border-white/20 text-white/80 hover:bg-white/20 hover:text-white transition-all text-xs font-medium"
    :title="i18n.t.search.placeholder">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
    </svg>
    <span class="hidden sm:inline">{{ i18n.t.search.placeholder }}</span>
    <kbd class="hidden md:inline-flex items-center px-1.5 py-0.5 rounded bg-white/10 text-[10px] font-mono border border-white/20">⌘/</kbd>
  </button>

  <!-- Modal de recherche -->
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4" @click.self="isOpen = false">
      <!-- Overlay -->
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="isOpen = false"></div>

      <!-- Search box -->
      <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-200"
        :class="isSearching ? 'ring-2 ring-blue-500' : ''">
        <!-- Input -->
        <div class="flex items-center gap-3 px-5 py-4 border-b border-gray-100">
          <svg class="w-5 h-5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input id="global-search-input" v-model="query" type="text"
            class="flex-1 text-base outline-none text-gray-900 placeholder-gray-400"
            :placeholder="i18n.t.search.placeholder"
            @input="isSearching = true" />
          <button @click="isOpen = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Results -->
        <div class="max-h-96 overflow-y-auto">
          <!-- Suggestions récentes -->
          <div v-if="!query.trim()" class="p-4">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">🕐 Recherches récentes</p>
            <div class="space-y-1">
              <div v-for="(s, i) in recentSearches" :key="i"
                class="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-gray-50 cursor-pointer transition-colors">
                <span class="text-lg">{{ s.icon }}</span>
                <span class="text-sm text-gray-700 flex-1">{{ s.label }}</span>
                <span class="text-xs text-gray-400">{{ s.time }}</span>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-100">
              <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">💡 Astuces</p>
              <ul class="space-y-1.5 text-xs text-gray-500">
                <li>• Appuyez sur <kbd class="px-1.5 py-0.5 bg-gray-100 rounded font-mono text-[10px]">/</kbd> pour ouvrir la recherche</li>
                <li>• Tapez un nom de patient, médecin ou examen</li>
                <li>• Utilisez les filtres pour affiner vos résultats</li>
              </ul>
            </div>
          </div>

          <!-- Résultats -->
          <div v-else-if="filteredResults.length" class="p-2">
            <p class="text-xs font-bold text-gray-500 px-3 py-2">{{ i18n.t.search.results }} ({{ filteredResults.length }})</p>
            <div v-for="r in filteredResults" :key="r.id"
              class="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-blue-50 cursor-pointer transition-colors">
              <span class="text-xl">{{ r.icon }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-900">{{ r.label }}</p>
                <p class="text-xs text-gray-500 truncate">{{ r.sublabel }}</p>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </div>
          </div>

          <!-- Aucun résultat -->
          <div v-else class="p-8 text-center">
            <span class="text-4xl block mb-3">🔍</span>
            <p class="text-sm font-semibold text-gray-700">{{ i18n.t.search.noResults }}</p>
            <p class="text-xs text-gray-500 mt-1">Essayez avec d'autres termes de recherche</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between text-[10px] text-gray-400">
          <span>⌘K pour focus · Esc pour fermer</span>
          <span>{{ filteredResults.length }} {{ i18n.t.search.results.toLowerCase() }}</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>
