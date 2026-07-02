<script setup>
import { ref, computed, reactive } from 'vue'

const search = ref('')
const activeTab = ref('actifs')
const showModal = ref(false)
const showDetailModal = ref(false)
const selectedPassage = ref(null)

const newPassage = reactive({ patient: '', age: '', triage: 'P2', motif: '', mode: 'Autonome', tension: '', fc: '', spo2: '' })
const modesArrivee = ['Autonome', 'Ambulance', 'SMUR', 'Police', 'Famille']

function ajouterPassage() {
  if (!newPassage.patient || !newPassage.motif) return
  passages.value.unshift({
    id: Date.now(), patient: newPassage.patient, age: Number(newPassage.age) || 0,
    triage: newPassage.triage, statut: 'En attente', motif: newPassage.motif,
    arrivee: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    attente: 0, tension: newPassage.tension || '---', fc: Number(newPassage.fc) || 0,
    spo2: Number(newPassage.spo2) || 98, glasgow: 15, medecin: '-', mode: newPassage.mode,
  })
  Object.assign(newPassage, { patient: '', age: '', triage: 'P2', motif: '', mode: 'Autonome', tension: '', fc: '', spo2: '' })
  showModal.value = false
}

const passages = ref([
  { id: 1, patient: 'Sylla Oumou', age: 38, triage: 'P1', statut: 'En cours', motif: 'Douleurs thoraciques intenses', arrivee: '08:12', attente: 8, tension: '160/100', fc: 112, spo2: 94, glasgow: 15, medecin: 'Dr. Camara', mode: 'SMUR' },
  { id: 2, patient: 'Diallo Mamadou', age: 45, triage: 'P2', statut: 'En attente', motif: 'Fièvre 40°C + convulsions', arrivee: '09:05', attente: 22, tension: '130/85', fc: 98, spo2: 97, glasgow: 14, medecin: '-', mode: 'Ambulance' },
  { id: 3, patient: 'Koné Ibrahim', age: 67, triage: 'P2', statut: 'En cours', motif: 'AVC suspecté — hémiplégie droite', arrivee: '09:30', attente: 5, tension: '180/110', fc: 88, spo2: 96, glasgow: 13, medecin: 'Dr. Bah', mode: 'SMUR' },
  { id: 4, patient: 'Traoré Aminata', age: 28, triage: 'P3', statut: 'En attente', motif: 'Fracture cheville droite', arrivee: '10:15', attente: 45, tension: '120/75', fc: 82, spo2: 99, glasgow: 15, medecin: '-', mode: 'Autonome' },
  { id: 5, patient: 'Bah Sekou', age: 52, triage: 'P3', statut: 'Hospitalisé', motif: 'Crise hypertensive', arrivee: '07:45', attente: 12, tension: '200/120', fc: 95, spo2: 98, glasgow: 15, medecin: 'Dr. Diallo', mode: 'Autonome' },
  { id: 6, patient: 'Camara Fatoumata', age: 19, triage: 'P4', statut: 'En attente', motif: 'Plaie superficielle main', arrivee: '10:45', attente: 60, tension: '115/70', fc: 76, spo2: 99, glasgow: 15, medecin: '-', mode: 'Autonome' },
])

const triageConfig = {
  P1: { label: 'P1 — Urgence absolue', color: 'bg-red-600 text-white', dot: 'bg-red-600', border: 'border-red-300 bg-red-50' },
  P2: { label: 'P2 — Urgence relative', color: 'bg-orange-500 text-white', dot: 'bg-orange-500', border: 'border-orange-300 bg-orange-50' },
  P3: { label: 'P3 — Urgence différée', color: 'bg-yellow-400 text-gray-900', dot: 'bg-yellow-400', border: 'border-yellow-300 bg-yellow-50' },
  P4: { label: 'P4 — Non urgent', color: 'bg-green-500 text-white', dot: 'bg-green-500', border: 'border-green-300 bg-green-50' },
}

const statutColor = {
  'En cours': 'badge-chu',
  'En attente': 'badge-warning',
  'Hospitalisé': 'badge-info',
  'Sorti': 'badge-success',
  'Transféré': 'badge-violet',
}

const stats = computed(() => ({
  total: passages.value.length,
  p1: passages.value.filter(p => p.triage === 'P1').length,
  p2: passages.value.filter(p => p.triage === 'P2').length,
  en_attente: passages.value.filter(p => p.statut === 'En attente').length,
  en_cours: passages.value.filter(p => p.statut === 'En cours').length,
  attente_moy: Math.round(passages.value.reduce((s, p) => s + p.attente, 0) / passages.value.length),
}))

const filtered = computed(() =>
  passages.value.filter(p =>
    p.patient.toLowerCase().includes(search.value.toLowerCase()) &&
    (activeTab.value === 'tous' || (activeTab.value === 'actifs' && ['En attente', 'En cours'].includes(p.statut)) ||
     (activeTab.value === 'sortis' && ['Hospitalisé', 'Sorti', 'Transféré'].includes(p.statut)))
  )
)

function openDetail(p) { selectedPassage.value = p; showDetailModal.value = true }

function spo2Color(v) {
  if (v < 90) return 'text-red-600 font-bold'
  if (v < 95) return 'text-orange-500 font-bold'
  return 'text-green-600'
}
function fcColor(v) {
  if (v > 120 || v < 50) return 'text-red-600 font-bold'
  if (v > 100) return 'text-orange-500'
  return 'text-gray-700'
}
</script>

<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">🚨 Urgences</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des passages aux urgences — Triage CCMU</p>
      </div>
      <button @click="showModal = true" class="btn-danger flex items-center gap-2">
        <span>+</span> Nouveau passage
      </button>
    </div>

    <!-- KPIs urgences -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div class="stat-card p-4 text-center border-l-4 border-red-500">
        <p class="text-2xl font-extrabold text-red-600">{{ stats.p1 }}</p>
        <p class="text-xs text-gray-500 mt-0.5">P1 — Critiques</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-orange-500">
        <p class="text-2xl font-extrabold text-orange-500">{{ stats.p2 }}</p>
        <p class="text-xs text-gray-500 mt-0.5">P2 — Urgents</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-amber-400">
        <p class="text-2xl font-extrabold text-amber-600">{{ stats.en_attente }}</p>
        <p class="text-xs text-gray-500 mt-0.5">En attente</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-blue-500">
        <p class="text-2xl font-extrabold text-blue-600">{{ stats.en_cours }}</p>
        <p class="text-xs text-gray-500 mt-0.5">En cours</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-gray-400">
        <p class="text-2xl font-extrabold text-gray-700">{{ stats.total }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Total du jour</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-green-500">
        <p class="text-2xl font-extrabold text-green-600">{{ stats.attente_moy }}<span class="text-sm font-normal">min</span></p>
        <p class="text-xs text-gray-500 mt-0.5">Attente moy.</p>
      </div>
    </div>

    <!-- Alerte P1 -->
    <div v-if="stats.p1 > 0" class="alert-critical flex items-center gap-3">
      <span class="text-red-600 font-bold text-sm shrink-0 pulse-dot">🚨 URGENCES P1 ACTIVES :</span>
      <div class="flex flex-wrap gap-2">
        <span v-for="p in passages.filter(x => x.triage === 'P1' && x.statut !== 'Sorti')" :key="p.id"
          class="text-xs font-bold bg-red-100 text-red-800 px-3 py-1 rounded-full">
          {{ p.patient }} — {{ p.motif }}
        </span>
      </div>
    </div>

    <!-- Tabs + Search -->
    <div class="stat-card p-4 flex flex-col sm:flex-row gap-3 items-start sm:items-center">
      <div class="flex gap-1 bg-gray-100 rounded-lg p-1">
        <button v-for="tab in [{k:'actifs',l:'Actifs'},{k:'tous',l:'Tous'},{k:'sortis',l:'Sortis/Hospitalisés'}]" :key="tab.k"
          @click="activeTab = tab.k"
          :class="['px-3 py-1.5 rounded-md text-xs font-semibold transition-all', activeTab === tab.k ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-700']">
          {{ tab.l }}
        </button>
      </div>
      <input v-model="search" class="input-field sm:max-w-xs" placeholder="🔍  Rechercher un patient..." />
    </div>

    <!-- Table passages -->
    <div class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Triage</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Patient</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Motif</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Constantes</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Arrivée</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Attente</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id"
              :class="['table-row border-b border-gray-50', p.triage === 'P1' ? 'bg-red-50/30' : p.triage === 'P2' ? 'bg-orange-50/20' : '']">
              <td class="px-4 py-3">
                <span :class="['text-xs font-bold px-2.5 py-1 rounded-full', triageConfig[p.triage]?.color]">
                  {{ p.triage }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div>
                  <p class="font-semibold text-gray-900">{{ p.patient }}</p>
                  <p class="text-xs text-gray-400">{{ p.age }} ans · {{ p.mode }}</p>
                </div>
              </td>
              <td class="px-4 py-3 text-xs text-gray-600 max-w-[200px]">{{ p.motif }}</td>
              <td class="px-4 py-3">
                <div class="text-xs space-y-0.5">
                  <p class="text-gray-600">TA: <span class="font-semibold">{{ p.tension }}</span></p>
                  <p>FC: <span :class="['font-semibold', fcColor(p.fc)]">{{ p.fc }} bpm</span></p>
                  <p>SpO₂: <span :class="[spo2Color(p.spo2)]">{{ p.spo2 }}%</span></p>
                </div>
              </td>
              <td class="px-4 py-3 text-xs font-mono text-gray-600">{{ p.arrivee }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', p.attente > 30 ? 'bg-red-100 text-red-700' : p.attente > 15 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700']">
                  {{ p.attente }} min
                </span>
              </td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[p.statut] || 'badge-info']">
                  {{ p.statut }}
                </span>
              </td>
              <td class="px-4 py-3">
                <button @click="openDetail(p)" class="text-blue-600 hover:text-blue-800 text-xs font-medium">Voir →</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal nouveau passage -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box modal-box-lg">
          <h3 class="text-lg font-bold text-gray-900 mb-5">🚨 Enregistrer un nouveau passage</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Nom du patient *</label>
              <input v-model="newPassage.patient" class="input-field" placeholder="Nom Prénom" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Âge</label>
              <input v-model="newPassage.age" type="number" class="input-field" placeholder="35" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Niveau de triage *</label>
              <select v-model="newPassage.triage" class="input-field">
                <option v-for="t in ['P1','P2','P3','P4']" :key="t" :value="t">{{ t }} — {{ { P1:'Urgence absolue', P2:'Urgence relative', P3:'Urgence différée', P4:'Non urgent' }[t] }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Mode d'arrivée</label>
              <select v-model="newPassage.mode" class="input-field">
                <option v-for="m in modesArrivee" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-semibold text-gray-600 mb-1">Motif de consultation *</label>
              <input v-model="newPassage.motif" class="input-field" placeholder="Décrivez le motif de venue aux urgences" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Tension artérielle</label>
              <input v-model="newPassage.tension" class="input-field" placeholder="120/80" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Fréquence cardiaque</label>
              <input v-model="newPassage.fc" type="number" class="input-field" placeholder="80" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">SpO₂ (%)</label>
              <input v-model="newPassage.spo2" type="number" class="input-field" placeholder="98" />
            </div>
          </div>
          <div class="flex gap-3 mt-5">
            <button @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterPassage" class="btn-danger flex-1">✅ Enregistrer le passage</button>
          </div>
        </div>
      </div>
    </Teleport>
    <Teleport to="body">
      <div v-if="showDetailModal && selectedPassage" class="modal-overlay" @click.self="showDetailModal = false">
        <div class="modal-box modal-box-lg">
          <div class="flex items-center justify-between mb-5">
            <div class="flex items-center gap-3">
              <span :class="['text-sm font-bold px-3 py-1.5 rounded-full', triageConfig[selectedPassage.triage]?.color]">
                {{ selectedPassage.triage }}
              </span>
              <h3 class="text-lg font-bold text-gray-900">{{ selectedPassage.patient }}</h3>
            </div>
            <button @click="showDetailModal = false" class="text-gray-400 hover:text-gray-600 text-xl">×</button>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-5">
            <div class="stat-card p-4">
              <p class="text-xs font-semibold text-gray-500 mb-2">CONSTANTES VITALES</p>
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">Tension artérielle</span>
                  <span class="font-bold">{{ selectedPassage.tension }} mmHg</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">Fréquence cardiaque</span>
                  <span :class="['font-bold', fcColor(selectedPassage.fc)]">{{ selectedPassage.fc }} bpm</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">SpO₂</span>
                  <span :class="['font-bold', spo2Color(selectedPassage.spo2)]">{{ selectedPassage.spo2 }}%</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">Score Glasgow</span>
                  <span class="font-bold">{{ selectedPassage.glasgow }}/15</span>
                </div>
              </div>
            </div>
            <div class="stat-card p-4">
              <p class="text-xs font-semibold text-gray-500 mb-2">INFORMATIONS</p>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Arrivée</span>
                  <span class="font-semibold">{{ selectedPassage.arrivee }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Mode d'arrivée</span>
                  <span class="font-semibold">{{ selectedPassage.mode }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Médecin</span>
                  <span class="font-semibold">{{ selectedPassage.medecin }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Statut</span>
                  <span :class="['text-xs font-medium px-2 py-0.5 rounded-full', statutColor[selectedPassage.statut]]">
                    {{ selectedPassage.statut }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card p-4 mb-4">
            <p class="text-xs font-semibold text-gray-500 mb-1">MOTIF DE CONSULTATION</p>
            <p class="text-sm text-gray-800">{{ selectedPassage.motif }}</p>
          </div>

          <div class="flex gap-3">
            <button class="btn-primary flex-1">Prendre en charge</button>
            <button class="btn-secondary flex-1">Hospitaliser</button>
            <button class="btn-secondary">Prescrire</button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>
