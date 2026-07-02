<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const showModal = ref(false)

const consultations = ref([
  { id: 1, patient: 'Diallo Mamadou', medecin: 'Dr. Camara', date: '2025-06-12', motif: 'Fièvre persistante', diagnostic: 'Paludisme (B54)', statut: 'Terminée' },
  { id: 2, patient: 'Bah Aissatou', medecin: 'Dr. Bah', date: '2025-06-12', motif: 'Grossesse 7 mois', diagnostic: 'Grossesse normale (Z34)', statut: 'En cours' },
  { id: 3, patient: 'Camara Sekou', medecin: 'Dr. Diallo', date: '2025-06-12', motif: 'Contrôle HTA', diagnostic: 'HTA essentielle (I10)', statut: 'En attente' },
  { id: 4, patient: 'Sylla Oumou', medecin: 'Dr. Camara', date: '2025-06-11', motif: 'Douleurs abdominales', diagnostic: 'Gastrite (K29)', statut: 'Terminée' },
])

const filtered = computed(() =>
  consultations.value.filter(c =>
    c.patient.toLowerCase().includes(search.value.toLowerCase()) ||
    c.medecin.toLowerCase().includes(search.value.toLowerCase())
  )
)

const statutColor = { 'Terminée': 'badge-success', 'En cours': 'badge-violet', 'En attente': 'badge-warning' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Consultations</h2>
        <p class="text-sm text-gray-500 mt-0.5">{{ filtered.length }} consultation(s)</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Nouvelle consultation</button>
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
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Médecin</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Motif</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Diagnostic (CIM-10)</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filtered" :key="c.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ c.patient }}</td>
              <td class="px-4 py-3 text-gray-600">{{ c.medecin }}</td>
              <td class="px-4 py-3 text-gray-500">{{ c.date }}</td>
              <td class="px-4 py-3 text-gray-600">{{ c.motif }}</td>
              <td class="px-4 py-3"><span class="badge-info text-xs px-2.5 py-1 rounded-full font-medium">{{ c.diagnostic }}</span></td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[c.statut]]">{{ c.statut }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-bold text-gray-900 mb-5">Nouvelle consultation</h3>
          <form @submit.prevent="showModal = false" class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Patient</label>
              <input class="input-field" placeholder="Rechercher un patient..." required />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Médecin</label>
                <input class="input-field" placeholder="Dr. ..." required />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Date</label>
                <input type="date" class="input-field" required />
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Motif</label>
              <input class="input-field" required />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Diagnostic (CIM-10)</label>
              <input class="input-field" placeholder="Ex: B54 - Paludisme" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Prescription</label>
              <textarea class="input-field" rows="3" placeholder="Médicaments, posologie..."></textarea>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1">Enregistrer</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
