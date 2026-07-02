<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const activeFilter = ref('Tous')
const showModal = ref(false)

const examens = ref([
  { id: 1, patient: 'Diallo Mamadou', modalite: 'Radiographie', region: 'Thorax', prescripteur: 'Dr. Camara', date: '2025-06-12', urgence: 'Urgent', statut: 'Réalisé', radiologue: 'Dr. Kouyaté', conclusion: 'Opacité basale droite' },
  { id: 2, patient: 'Koné Fatoumata', modalite: 'Scanner', region: 'Abdomen', prescripteur: 'Dr. Bah', date: '2025-06-12', urgence: 'Normal', statut: 'Prescrit', radiologue: '-', conclusion: '' },
  { id: 3, patient: 'Traoré Ibrahim', modalite: 'IRM', region: 'Cerveau', prescripteur: 'Dr. Diallo', date: '2025-06-11', urgence: 'STAT', statut: 'Validé', radiologue: 'Dr. Kouyaté', conclusion: 'Ischémie sylvienne gauche' },
  { id: 4, patient: 'Sylla Oumou', modalite: 'Échographie', region: 'Abdomen pelvis', prescripteur: 'Dr. Camara', date: '2025-06-11', urgence: 'Normal', statut: 'Interprété', radiologue: 'Dr. Kouyaté', conclusion: 'Lithiase vésiculaire' },
  { id: 5, patient: 'Bah Aissatou', modalite: 'Mammographie', region: 'Sein bilatéral', prescripteur: 'Dr. Bah', date: '2025-06-10', urgence: 'Normal', statut: 'Planifié', radiologue: '-', conclusion: '' },
])

const modalites = ['Radiographie', 'Scanner', 'IRM', 'Échographie', 'Mammographie', 'Scintigraphie', 'PET-Scan']
const statuts = ['Tous', 'Prescrit', 'Planifié', 'En cours', 'Réalisé', 'Interprété', 'Validé']

const filtered = computed(() =>
  examens.value.filter(e =>
    (activeFilter.value === 'Tous' || e.statut === activeFilter.value) &&
    e.patient.toLowerCase().includes(search.value.toLowerCase())
  )
)

const urgenceColor = { 'Normal': 'badge-info', 'Urgent': 'badge-warning', 'STAT': 'badge-danger' }
const statutColor = {
  'Prescrit': 'badge-info', 'Planifié': 'badge-violet', 'En cours': 'badge-warning',
  'Réalisé': 'badge-teal', 'Interprété': 'badge-orange', 'Validé': 'badge-success',
}

const modaliteIcon = {
  'Radiographie': '🩻', 'Scanner': '🔬', 'IRM': '🧲', 'Échographie': '📡',
  'Mammographie': '🔍', 'Scintigraphie': '☢️', 'PET-Scan': '🫀',
}

const stats = computed(() => ({
  total: examens.value.length,
  stat: examens.value.filter(e => e.urgence === 'STAT').length,
  en_attente: examens.value.filter(e => ['Prescrit', 'Planifié'].includes(e.statut)).length,
  a_interpreter: examens.value.filter(e => e.statut === 'Réalisé').length,
}))
</script>

<template>
  <div class="space-y-5">

    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">🩻 Imagerie Médicale</h2>
        <p class="text-sm text-gray-500 mt-0.5">Radiologie, Scanner, IRM, Échographie</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Prescrire examen</button>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="stat-card p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-lg">🩻</div>
        <div><p class="text-xl font-extrabold text-gray-900">{{ stats.total }}</p><p class="text-xs text-gray-500">Total examens</p></div>
      </div>
      <div class="stat-card p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center text-lg">⚡</div>
        <div><p class="text-xl font-extrabold text-red-600">{{ stats.stat }}</p><p class="text-xs text-gray-500">STAT — Immédiats</p></div>
      </div>
      <div class="stat-card p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center text-lg">⏳</div>
        <div><p class="text-xl font-extrabold text-amber-600">{{ stats.en_attente }}</p><p class="text-xs text-gray-500">En attente</p></div>
      </div>
      <div class="stat-card p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-teal-100 flex items-center justify-center text-lg">📋</div>
        <div><p class="text-xl font-extrabold text-teal-600">{{ stats.a_interpreter }}</p><p class="text-xs text-gray-500">À interpréter</p></div>
      </div>
    </div>

    <!-- Modalités disponibles -->
    <div class="stat-card p-5">
      <p class="section-title mb-4">Modalités disponibles</p>
      <div class="grid grid-cols-3 sm:grid-cols-7 gap-3">
        <div v-for="m in modalites" :key="m"
          class="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-blue-50 hover:bg-blue-100 cursor-pointer transition-colors">
          <span class="text-2xl">{{ modaliteIcon[m] || '🔬' }}</span>
          <p class="text-xs font-semibold text-blue-800 text-center leading-tight">{{ m }}</p>
          <p class="text-xs text-blue-500">{{ examens.filter(e => e.modalite === m).length }} exam.</p>
        </div>
      </div>
    </div>

    <!-- Filtres -->
    <div class="stat-card p-4 flex flex-wrap gap-3 items-center">
      <input v-model="search" class="input-field max-w-xs" placeholder="🔍  Rechercher..." />
      <div class="flex gap-2 flex-wrap">
        <button v-for="s in statuts" :key="s" @click="activeFilter = s"
          :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
            activeFilter === s ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-700 hover:bg-blue-100']">
          {{ s }}
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
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Modalité</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Région</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Prescripteur</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Urgence</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Conclusion</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in filtered" :key="e.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ e.patient }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <span>{{ modaliteIcon[e.modalite] || '🔬' }}</span>
                  <span class="text-gray-700">{{ e.modalite }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ e.region }}</td>
              <td class="px-4 py-3 text-gray-500">{{ e.prescripteur }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', urgenceColor[e.urgence]]">{{ e.urgence }}</span>
              </td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[e.statut]]">{{ e.statut }}</span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-600 max-w-[180px] truncate">{{ e.conclusion || '—' }}</td>
              <td class="px-4 py-3">
                <button class="text-blue-600 hover:text-blue-800 text-xs font-medium">Traiter →</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal prescription -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-bold text-gray-900 mb-5">Prescrire un examen d'imagerie</h3>
          <form @submit.prevent="showModal = false" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Patient</label>
                <select class="input-field">
                  <option>Diallo Mamadou</option>
                  <option>Koné Fatoumata</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Modalité</label>
                <select class="input-field">
                  <option v-for="m in modalites" :key="m">{{ m }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Région anatomique</label>
                <input class="input-field" placeholder="Ex: Thorax, Abdomen..." required />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Urgence</label>
                <select class="input-field">
                  <option>Normal</option>
                  <option>Urgent</option>
                  <option>STAT</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Indication clinique</label>
              <textarea class="input-field" rows="3" placeholder="Contexte clinique, hypothèse diagnostique..." required></textarea>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1">Prescrire</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>
