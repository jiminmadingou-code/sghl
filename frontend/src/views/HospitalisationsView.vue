<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const showModal = ref(false)

const hospitalisations = ref([
  { id: 1, patient: 'Koné Fatoumata', service: 'Médecine interne', chambre: 'C-12', lit: 'L-02', medecin: 'Dr. Camara', entree: '2025-06-08', sortie_prev: '2025-06-15', statut: 'Actif' },
  { id: 2, patient: 'Traoré Ibrahim', service: 'Cardiologie', chambre: 'C-05', lit: 'L-01', medecin: 'Dr. Bah', entree: '2025-06-10', sortie_prev: '2025-06-18', statut: 'Actif' },
  { id: 3, patient: 'Sylla Oumou', service: 'Maternité', chambre: 'M-03', lit: 'L-04', medecin: 'Dr. Diallo', entree: '2025-06-11', sortie_prev: '2025-06-13', statut: 'Sorti' },
])

const services = ['Médecine interne', 'Cardiologie', 'Maternité', 'Chirurgie', 'Pédiatrie', 'Urgences']

const filtered = computed(() =>
  hospitalisations.value.filter(h =>
    h.patient.toLowerCase().includes(search.value.toLowerCase())
  )
)

const stats = [
  { label: 'Hospitalisations actives', value: 2, icon: '🏥', color: 'bg-violet-100' },
  { label: 'Sorties aujourd\'hui', value: 1, icon: '🚪', color: 'bg-green-100' },
  { label: 'Lits disponibles', value: 33, icon: '🛏', color: 'bg-blue-100' },
  { label: 'Transferts en cours', value: 0, icon: '🔄', color: 'bg-amber-100' },
]
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Hospitalisations</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des admissions et séjours</p>
      </div>
      <button @click="showModal = true" class="btn-primary flex items-center gap-2">+ Nouvelle admission</button>
    </div>

    <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="s in stats" :key="s.label" class="stat-card p-4 card-hover">
        <div :class="['kpi-icon mb-2', s.color]">{{ s.icon }}</div>
        <p class="text-2xl font-bold text-gray-900">{{ s.value }}</p>
        <p class="text-xs text-gray-500 mt-0.5">{{ s.label }}</p>
      </div>
    </div>

    <div class="stat-card p-4">
      <input v-model="search" class="input-field max-w-xs" placeholder="🔍  Rechercher..." />
    </div>

    <div class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Patient</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Service</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Chambre / Lit</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Médecin référent</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Entrée</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Sortie prév.</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in filtered" :key="h.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ h.patient }}</td>
              <td class="px-4 py-3 text-gray-600">{{ h.service }}</td>
              <td class="px-4 py-3">
                <span class="badge-violet text-xs px-2.5 py-1 rounded-full font-medium">{{ h.chambre }} · {{ h.lit }}</span>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ h.medecin }}</td>
              <td class="px-4 py-3 text-gray-600">{{ h.entree }}</td>
              <td class="px-4 py-3 text-gray-600">{{ h.sortie_prev }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', h.statut === 'Actif' ? 'badge-success' : 'badge-violet']">
                  {{ h.statut }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-bold text-gray-900 mb-5">Nouvelle admission</h3>
          <form @submit.prevent="showModal = false" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="col-span-2">
                <label class="block text-xs font-medium text-gray-600 mb-1">Patient</label>
                <input class="input-field" placeholder="Rechercher un patient..." required />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Service</label>
                <select class="input-field">
                  <option v-for="s in services" :key="s">{{ s }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Médecin référent</label>
                <input class="input-field" placeholder="Dr. ..." required />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Date d'entrée</label>
                <input type="date" class="input-field" required />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Sortie prévisionnelle</label>
                <input type="date" class="input-field" />
              </div>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1">Admettre</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
