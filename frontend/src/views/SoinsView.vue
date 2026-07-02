<script setup>
import { ref, computed, reactive } from 'vue'

const activePatient = ref(1)
const showConstantesModal = ref(false)
const showSoinModal = ref(false)

const newConstante = reactive({ ta: '', pouls: '', temp: '', spo2: '', glycemie: '' })
const newSoin = reactive({ heure: '', type: 'Médicament', description: '' })

const typesSoin = ['Médicament', 'Pansement', 'Surveillance', 'Injection', 'Perfusion', 'Kinésithérapie']

function ajouterConstante() {
  if (!newConstante.ta || !newConstante.pouls) return
  const now = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  constantes.value[activePatient.value].push({
    heure: now,
    ta: newConstante.ta, pouls: Number(newConstante.pouls),
    temp: Number(newConstante.temp) || 37.0,
    spo2: Number(newConstante.spo2) || 98,
    glycemie: Number(newConstante.glycemie) || 1.0,
  })
  Object.assign(newConstante, { ta: '', pouls: '', temp: '', spo2: '', glycemie: '' })
  showConstantesModal.value = false
}

function ajouterSoin() {
  if (!newSoin.heure || !newSoin.description) return
  soins.value.push({
    id: Date.now(), patientId: activePatient.value,
    heure: newSoin.heure, type: newSoin.type,
    description: newSoin.description, statut: 'Planifié', infirmier: 'Inf. (vous)',
  })
  Object.assign(newSoin, { heure: '', type: 'Médicament', description: '' })
  showSoinModal.value = false
}

const patients = ref([
  { id: 1, nom: 'Koné Fatoumata',  service: 'Médecine interne', lit: 'C-12/L-02', medecin: 'Dr. Camara', statut: 'stable' },
  { id: 2, nom: 'Traoré Ibrahim',  service: 'Cardiologie',       lit: 'C-05/L-01', medecin: 'Dr. Bah',    statut: 'critique' },
  { id: 3, nom: 'Diallo Mamadou',  service: 'Médecine interne', lit: 'C-08/L-03', medecin: 'Dr. Camara', statut: 'stable' },
])

const constantes = ref({
  1: [
    { heure: '06:00', ta: '120/80', pouls: 72, temp: 37.2, spo2: 98, glycemie: 1.1 },
    { heure: '10:00', ta: '118/78', pouls: 74, temp: 37.4, spo2: 97, glycemie: 1.3 },
    { heure: '14:00', ta: '122/82', pouls: 76, temp: 37.1, spo2: 98, glycemie: 1.2 },
    { heure: '18:00', ta: '119/79', pouls: 73, temp: 37.3, spo2: 99, glycemie: 1.0 },
  ],
  2: [
    { heure: '06:00', ta: '160/100', pouls: 95, temp: 38.5, spo2: 92, glycemie: 2.1 },
    { heure: '10:00', ta: '155/98',  pouls: 98, temp: 38.8, spo2: 91, glycemie: 2.4 },
    { heure: '14:00', ta: '162/102', pouls: 102, temp: 39.1, spo2: 90, glycemie: 2.6 },
    { heure: '18:00', ta: '158/99',  pouls: 99, temp: 38.9, spo2: 91, glycemie: 2.3 },
  ],
  3: [
    { heure: '06:00', ta: '130/85', pouls: 80, temp: 37.8, spo2: 96, glycemie: 1.8 },
    { heure: '10:00', ta: '128/84', pouls: 78, temp: 37.6, spo2: 97, glycemie: 1.6 },
    { heure: '14:00', ta: '132/86', pouls: 82, temp: 37.9, spo2: 96, glycemie: 1.9 },
    { heure: '18:00', ta: '129/83', pouls: 79, temp: 37.7, spo2: 97, glycemie: 1.7 },
  ],
})

const soins = ref([
  { id: 1, patientId: 1, heure: '08:00', type: 'Médicament', description: 'Amlodipine 5mg — voie orale', statut: 'Effectué', infirmier: 'Inf. Kouyaté' },
  { id: 2, patientId: 1, heure: '12:00', type: 'Pansement', description: 'Changement pansement plaie opératoire', statut: 'Planifié', infirmier: 'Inf. Kouyaté' },
  { id: 3, patientId: 2, heure: '08:00', type: 'Médicament', description: 'Furosémide 40mg IV', statut: 'Effectué', infirmier: 'Inf. Traoré' },
  { id: 4, patientId: 2, heure: '10:00', type: 'Surveillance', description: 'Contrôle TA + SpO2 toutes les 2h', statut: 'En cours', infirmier: 'Inf. Traoré' },
  { id: 5, patientId: 2, heure: '14:00', type: 'Médicament', description: 'Amiodarone 200mg — OMIS', statut: 'Omis', infirmier: '-' },
])

const currentPatient = computed(() => patients.value.find(p => p.id === activePatient.value))
const currentConstantes = computed(() => constantes.value[activePatient.value] || [])
const currentSoins = computed(() => soins.value.filter(s => s.patientId === activePatient.value))
const lastConstante = computed(() => currentConstantes.value[currentConstantes.value.length - 1])

function vitalStatus(key, val) {
  const thresholds = {
    pouls:   { ok: [60, 100], warn: [50, 110] },
    temp:    { ok: [36.5, 37.5], warn: [36, 38] },
    spo2:    { ok: [95, 100], warn: [90, 94] },
    glycemie:{ ok: [0.7, 1.4], warn: [0.6, 2.0] },
  }
  if (!thresholds[key]) return 'normal'
  const { ok, warn } = thresholds[key]
  if (val >= ok[0] && val <= ok[1]) return 'normal'
  if (val >= warn[0] && val <= warn[1]) return 'warning'
  return 'critical'
}

function sparkPouls(arr) { return arr.map(c => c.pouls) }
function sparkMax(arr) { return Math.max(...arr) }
function sparkMin(arr) { return Math.min(...arr) }
function sparkH(v, arr) { return Math.round(((v - sparkMin(arr)) / (sparkMax(arr) - sparkMin(arr) + 1)) * 80 + 10) }

const soinStatutColor = {
  'Effectué': 'badge-success',
  'Planifié': 'badge-info',
  'En cours': 'badge-violet',
  'Omis':     'badge-danger',
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Soins Infirmiers</h2>
        <p class="text-sm text-gray-500 mt-0.5">Constantes vitales · Planification des soins · Alertes</p>
      </div>
      <button @click="showConstantesModal = true" class="btn-primary">+ Saisir constantes</button>
    </div>

    <!-- Alerte critique -->
    <div v-if="patients.some(p => p.statut === 'critique')" class="alert-critical flex items-center gap-3">
      <span class="text-red-700 font-bold text-sm shrink-0">⚠ Patient(s) en état critique :</span>
      <span v-for="p in patients.filter(p => p.statut === 'critique')" :key="p.id"
        class="text-xs font-bold bg-red-100 text-red-800 px-3 py-1 rounded-full">
        {{ p.nom }} — {{ p.service }}
      </span>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-4 gap-4">

      <!-- Patient list -->
      <div class="stat-card p-4 space-y-2">
        <p class="section-title mb-3">Patients hospitalisés</p>
        <button
          v-for="p in patients" :key="p.id"
          @click="activePatient = p.id"
          :class="['w-full text-left p-3 rounded-xl border-2 transition-all',
            activePatient === p.id ? 'border-violet-500 bg-violet-50' : 'border-transparent bg-gray-50 hover:bg-violet-50/50']"
        >
          <div class="flex items-center gap-2.5">
            <div :class="['w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0',
              p.statut === 'critique' ? 'bg-red-100 text-red-700' : 'bg-violet-100 text-violet-700']">
              {{ p.nom.split(' ').map(n=>n[0]).join('') }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-gray-900 truncate">{{ p.nom }}</p>
              <p class="text-[10px] text-gray-500">{{ p.lit }}</p>
            </div>
            <span :class="['text-[10px] font-bold px-1.5 py-0.5 rounded-full',
              p.statut === 'critique' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700']">
              {{ p.statut }}
            </span>
          </div>
        </button>
      </div>

      <!-- Main content -->
      <div class="xl:col-span-3 space-y-4" v-if="currentPatient">

        <!-- Patient header -->
        <div class="stat-card p-4 flex items-center gap-4">
          <div :class="['w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-lg shrink-0',
            currentPatient.statut === 'critique' ? 'bg-red-100 text-red-700' : 'bg-violet-100 text-violet-700']">
            {{ currentPatient.nom.split(' ').map(n=>n[0]).join('') }}
          </div>
          <div class="flex-1">
            <h3 class="font-bold text-gray-900">{{ currentPatient.nom }}</h3>
            <p class="text-sm text-gray-500">{{ currentPatient.service }} · {{ currentPatient.lit }} · {{ currentPatient.medecin }}</p>
          </div>
          <span :class="['text-xs font-bold px-3 py-1.5 rounded-full',
            currentPatient.statut === 'critique' ? 'badge-danger' : 'badge-success']">
            {{ currentPatient.statut.toUpperCase() }}
          </span>
        </div>

        <!-- Constantes vitales actuelles -->
        <div v-if="lastConstante" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div :class="['vital-card', vitalStatus('pouls', lastConstante.pouls)]">
            <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Pouls</p>
            <p class="text-2xl font-extrabold text-gray-900">{{ lastConstante.pouls }}</p>
            <p class="text-xs text-gray-500">bpm</p>
            <div class="sparkline mt-2 justify-center">
              <div v-for="(v, i) in sparkPouls(currentConstantes)" :key="i"
                :class="['sparkline-bar', i === currentConstantes.length-1 ? 'active' : '']"
                :style="{ height: sparkH(v, sparkPouls(currentConstantes)) + '%' }">
              </div>
            </div>
          </div>
          <div :class="['vital-card', vitalStatus('temp', lastConstante.temp)]">
            <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Température</p>
            <p class="text-2xl font-extrabold text-gray-900">{{ lastConstante.temp }}</p>
            <p class="text-xs text-gray-500">°C</p>
            <p :class="['text-xs font-bold mt-2', lastConstante.temp > 38 ? 'text-red-600' : 'text-green-600']">
              {{ lastConstante.temp > 38 ? '🔴 Fièvre' : '🟢 Normal' }}
            </p>
          </div>
          <div :class="['vital-card', vitalStatus('spo2', lastConstante.spo2)]">
            <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1">SpO₂</p>
            <p class="text-2xl font-extrabold text-gray-900">{{ lastConstante.spo2 }}</p>
            <p class="text-xs text-gray-500">%</p>
            <p :class="['text-xs font-bold mt-2', lastConstante.spo2 < 94 ? 'text-red-600' : 'text-green-600']">
              {{ lastConstante.spo2 < 94 ? '🔴 Critique' : '🟢 Normal' }}
            </p>
          </div>
          <div :class="['vital-card', vitalStatus('glycemie', lastConstante.glycemie)]">
            <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Glycémie</p>
            <p class="text-2xl font-extrabold text-gray-900">{{ lastConstante.glycemie }}</p>
            <p class="text-xs text-gray-500">g/L</p>
            <p :class="['text-xs font-bold mt-2', lastConstante.glycemie > 1.4 ? 'text-amber-600' : 'text-green-600']">
              {{ lastConstante.glycemie > 1.4 ? '🟡 Élevée' : '🟢 Normal' }}
            </p>
          </div>
        </div>

        <!-- Historique constantes -->
        <div class="stat-card p-5">
          <p class="section-title mb-4">Historique des constantes — {{ new Date().toLocaleDateString('fr-FR') }}</p>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="table-header">
                  <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500">Heure</th>
                  <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500">TA (mmHg)</th>
                  <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500">Pouls</th>
                  <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500">Temp.</th>
                  <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500">SpO₂</th>
                  <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500">Glycémie</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in currentConstantes" :key="c.heure" class="table-row border-b border-gray-50">
                  <td class="px-3 py-2.5 font-mono text-xs font-bold text-violet-700">{{ c.heure }}</td>
                  <td class="px-3 py-2.5 text-sm font-semibold text-gray-900">{{ c.ta }}</td>
                  <td class="px-3 py-2.5">
                    <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', vitalStatus('pouls', c.pouls) === 'normal' ? 'badge-success' : vitalStatus('pouls', c.pouls) === 'warning' ? 'badge-warning' : 'badge-danger']">
                      {{ c.pouls }} bpm
                    </span>
                  </td>
                  <td class="px-3 py-2.5">
                    <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', vitalStatus('temp', c.temp) === 'normal' ? 'badge-success' : vitalStatus('temp', c.temp) === 'warning' ? 'badge-warning' : 'badge-danger']">
                      {{ c.temp }}°C
                    </span>
                  </td>
                  <td class="px-3 py-2.5">
                    <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', vitalStatus('spo2', c.spo2) === 'normal' ? 'badge-success' : vitalStatus('spo2', c.spo2) === 'warning' ? 'badge-warning' : 'badge-danger']">
                      {{ c.spo2 }}%
                    </span>
                  </td>
                  <td class="px-3 py-2.5">
                    <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', vitalStatus('glycemie', c.glycemie) === 'normal' ? 'badge-success' : vitalStatus('glycemie', c.glycemie) === 'warning' ? 'badge-warning' : 'badge-danger']">
                      {{ c.glycemie }} g/L
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Plan de soins -->
        <div class="stat-card p-5">
          <div class="flex items-center justify-between mb-4">
            <p class="section-title">Plan de soins du jour</p>
            <button @click="showSoinModal = true" class="btn-primary text-xs py-1.5">+ Ajouter soin</button>
          </div>
          <div class="space-y-2">
            <div v-for="s in currentSoins" :key="s.id"
              :class="['flex items-center gap-4 p-3 rounded-xl border', s.statut === 'Omis' ? 'border-red-200 bg-red-50' : 'border-gray-100 bg-gray-50']">
              <div class="text-center shrink-0 w-12">
                <p class="text-xs font-bold text-violet-700 font-mono">{{ s.heure }}</p>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-900">{{ s.description }}</p>
                <p class="text-xs text-gray-500">{{ s.type }} · {{ s.infirmier }}</p>
              </div>
              <span :class="['text-xs font-bold px-2.5 py-1 rounded-full shrink-0', soinStatutColor[s.statut]]">
                {{ s.statut }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal saisir constantes -->
  <Teleport to="body">
    <div v-if="showConstantesModal" class="modal-overlay" @click.self="showConstantesModal = false">
      <div class="modal-box">
        <h3 class="text-lg font-bold text-gray-900 mb-1">Saisir constantes vitales</h3>
        <p class="text-sm text-gray-500 mb-4">Patient : {{ currentPatient?.nom }}</p>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Tension (ex: 120/80) *</label>
              <input v-model="newConstante.ta" class="input-field" placeholder="120/80" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Pouls (bpm) *</label>
              <input v-model="newConstante.pouls" type="number" class="input-field" placeholder="72" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Température (°C)</label>
              <input v-model="newConstante.temp" type="number" step="0.1" class="input-field" placeholder="37.2" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">SpO₂ (%)</label>
              <input v-model="newConstante.spo2" type="number" class="input-field" placeholder="98" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-semibold text-gray-600 mb-1">Glycémie (g/L)</label>
              <input v-model="newConstante.glycemie" type="number" step="0.1" class="input-field" placeholder="1.1" />
            </div>
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="showConstantesModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterConstante" class="btn-primary flex-1">✅ Enregistrer</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal ajouter soin -->
  <Teleport to="body">
    <div v-if="showSoinModal" class="modal-overlay" @click.self="showSoinModal = false">
      <div class="modal-box">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Ajouter un soin planifié</h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Heure *</label>
              <input v-model="newSoin.heure" type="time" class="input-field" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Type de soin</label>
              <select v-model="newSoin.type" class="input-field">
                <option v-for="t in typesSoin" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Description *</label>
            <input v-model="newSoin.description" class="input-field" placeholder="Description du soin à effectuer" />
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="showSoinModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterSoin" class="btn-primary flex-1">✅ Planifier</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
