<script setup>
import { ref, computed, reactive } from 'vue'

const search = ref('')
const activeFilter = ref('Tous')
const showModal = ref(false)
const showTraiterModal = ref(false)
const selectedExamen = ref(null)

const newExamen = reactive({ patient: '', type: '', prescripteur: '', priorite: 'Normal' })

const typesExamen = ['NFS', 'Glycémie', 'ECG', 'Radiographie', 'Urine ECBU', 'Ionogramme', 'Bilan hépatique', 'Sérologie']

function ajouterExamen() {
  if (!newExamen.patient || !newExamen.type) return
  examens.value.unshift({
    id: Date.now(), patient: newExamen.patient, type: newExamen.type,
    prescripteur: newExamen.prescripteur || 'Dr. (vous)', date: new Date().toISOString().slice(0,10),
    priorite: newExamen.priorite, statut: 'Commande', technicien: '-',
  })
  Object.assign(newExamen, { patient: '', type: '', prescripteur: '', priorite: 'Normal' })
  showModal.value = false
}

function ouvrirTraiter(examen) { selectedExamen.value = { ...examen }; showTraiterModal.value = true }

function avancerWorkflow() {
  const idx = workflow.indexOf(selectedExamen.value.statut)
  if (idx < workflow.length - 1) {
    const found = examens.value.find(e => e.id === selectedExamen.value.id)
    if (found) found.statut = workflow[idx + 1]
    selectedExamen.value.statut = workflow[idx + 1]
  }
  showTraiterModal.value = false
}

const examens = ref([
  { id: 1, patient: 'Diallo Mamadou', type: 'NFS', prescripteur: 'Dr. Camara', date: '2025-06-12', priorite: 'Urgent', statut: 'Prélèvement', technicien: 'Lab. Kouyaté' },
  { id: 2, patient: 'Koné Fatoumata', type: 'Glycémie', prescripteur: 'Dr. Bah', date: '2025-06-12', priorite: 'Normal', statut: 'Saisie résultats', technicien: 'Lab. Kouyaté' },
  { id: 3, patient: 'Traoré Ibrahim', type: 'ECG', prescripteur: 'Dr. Diallo', date: '2025-06-11', priorite: 'Normal', statut: 'Validé', technicien: 'Lab. Sylla' },
  { id: 4, patient: 'Camara Sekou', type: 'Radiographie', prescripteur: 'Dr. Camara', date: '2025-06-11', priorite: 'Urgent', statut: 'Publié', technicien: 'Lab. Sylla' },
  { id: 5, patient: 'Bah Aissatou', type: 'Urine ECBU', prescripteur: 'Dr. Bah', date: '2025-06-10', priorite: 'Normal', statut: 'Commande', technicien: '-' },
])

const workflow = ['Commande', 'Prélèvement', 'Affectation', 'Saisie résultats', 'Validé', 'Publié']

const filters = ['Tous', ...workflow]

const filtered = computed(() =>
  examens.value.filter(e =>
    (activeFilter.value === 'Tous' || e.statut === activeFilter.value) &&
    e.patient.toLowerCase().includes(search.value.toLowerCase())
  )
)

const statutColor = {
  'Commande': 'badge-info',
  'Prélèvement': 'badge-warning',
  'Affectation': 'badge-warning',
  'Saisie résultats': 'badge-violet',
  'Validé': 'badge-success',
  'Publié': 'badge-success',
}

function workflowStep(statut) {
  return workflow.indexOf(statut)
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Laboratoire (LIS)</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des examens biologiques</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Prescrire examen</button>
    </div>

    <!-- Workflow pipeline -->
    <div class="stat-card p-5">
      <p class="section-title mb-4">Pipeline des examens</p>
      <div class="flex items-center gap-0 overflow-x-auto">
        <div v-for="(step, i) in workflow" :key="step" class="flex items-center">
          <div class="flex flex-col items-center min-w-[100px]">
            <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold', i <= 3 ? 'bg-violet-600 text-white' : 'bg-violet-100 text-violet-600']">
              {{ i + 1 }}
            </div>
            <p class="text-xs text-center mt-1.5 font-medium text-gray-600 leading-tight">{{ step }}</p>
            <p class="text-xs text-violet-600 font-bold">{{ examens.filter(e => e.statut === step).length }}</p>
          </div>
          <div v-if="i < workflow.length - 1" class="w-8 h-0.5 bg-violet-200 mb-5"></div>
        </div>
      </div>
    </div>

    <!-- Filters + search -->
    <div class="stat-card p-4 flex flex-wrap gap-3 items-center">
      <input v-model="search" class="input-field max-w-xs" placeholder="🔍  Rechercher..." />
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="f in filters" :key="f"
          @click="activeFilter = f"
          :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all', activeFilter === f ? 'bg-violet-600 text-white' : 'bg-violet-50 text-violet-700 hover:bg-violet-100']"
        >
          {{ f }}
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Patient</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Type d'examen</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Prescripteur</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Priorité</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in filtered" :key="e.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ e.patient }}</td>
              <td class="px-4 py-3 text-gray-600">{{ e.type }}</td>
              <td class="px-4 py-3 text-gray-500">{{ e.prescripteur }}</td>
              <td class="px-4 py-3 text-gray-500">{{ e.date }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', e.priorite === 'Urgent' ? 'badge-danger' : 'badge-info']">
                  {{ e.priorite }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[e.statut]]">{{ e.statut }}</span>
              </td>
              <td class="px-4 py-3">
                <button @click="ouvrirTraiter(e)" class="text-violet-600 hover:text-violet-800 text-xs font-medium">Traiter →</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Modal prescrire examen -->
  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Prescrire un examen</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Patient *</label>
            <input v-model="newExamen.patient" class="input-field" placeholder="Nom du patient" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Type d'examen *</label>
              <select v-model="newExamen.type" class="input-field">
                <option value="">Sélectionner</option>
                <option v-for="t in typesExamen" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Priorité</label>
              <select v-model="newExamen.priorite" class="input-field">
                <option>Normal</option>
                <option>Urgent</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Prescripteur</label>
            <input v-model="newExamen.prescripteur" class="input-field" placeholder="Dr. ..." />
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterExamen" class="btn-primary flex-1">✅ Prescrire</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal traiter examen -->
  <Teleport to="body">
    <div v-if="showTraiterModal && selectedExamen" class="modal-overlay" @click.self="showTraiterModal = false">
      <div class="modal-box">
        <h3 class="text-lg font-bold text-gray-900 mb-1">Traiter l'examen</h3>
        <p class="text-sm text-gray-500 mb-4">{{ selectedExamen.patient }} — {{ selectedExamen.type }}</p>
        <div class="bg-blue-50 rounded-xl p-4 mb-4">
          <p class="text-xs font-semibold text-gray-500 mb-2">STATUT ACTUEL</p>
          <div class="flex items-center gap-3">
            <span :class="['text-sm font-bold px-3 py-1.5 rounded-full', statutColor[selectedExamen.statut]]">{{ selectedExamen.statut }}</span>
            <span class="text-gray-400">→</span>
            <span v-if="workflow.indexOf(selectedExamen.statut) < workflow.length - 1"
              class="text-sm font-bold px-3 py-1.5 rounded-full bg-green-100 text-green-700">
              {{ workflow[workflow.indexOf(selectedExamen.statut) + 1] }}
            </span>
            <span v-else class="text-xs text-green-600 font-semibold">✅ Terminé</span>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showTraiterModal = false" class="btn-secondary flex-1">Fermer</button>
          <button v-if="workflow.indexOf(selectedExamen.statut) < workflow.length - 1"
            @click="avancerWorkflow" class="btn-primary flex-1">▶ Avancer le statut</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
