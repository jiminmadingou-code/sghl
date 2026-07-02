<script setup>
import { ref, computed, onMounted } from 'vue'
import { gardesService, personnelService } from '@/services/sghl'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const showModal = ref(false)
const loading = ref(true)
const saving = ref(false)
const semaine = ref(0) // 0 = semaine courante

const gardes = ref([])
const personnel = ref([])
const typesGarde = ref([])

const form = ref({ personnel_id: '', type_garde_id: '', date_debut: '', date_fin: '', lieu: '', observations: '' })

const DEMO_GARDES = [
  { id: 1, personnel_id: 1, type_garde_id: 1, date_debut: '2025-06-12T07:00:00', date_fin: '2025-06-12T19:00:00', statut: 'confirmé', lieu: 'Urgences', observations: '', _nom: 'Dr. Camara', _type: 'Garde de jour', _couleur: 'bg-violet-100 border-violet-400 text-violet-800' },
  { id: 2, personnel_id: 2, type_garde_id: 2, date_debut: '2025-06-12T19:00:00', date_fin: '2025-06-13T07:00:00', statut: 'confirmé', lieu: 'Médecine interne', observations: '', _nom: 'Dr. Bah', _type: 'Garde de nuit', _couleur: 'bg-blue-100 border-blue-400 text-blue-800' },
  { id: 3, personnel_id: 3, type_garde_id: 1, date_debut: '2025-06-13T07:00:00', date_fin: '2025-06-13T19:00:00', statut: 'planifie', lieu: 'Maternité', observations: '', _nom: 'Dr. Diallo', _type: 'Garde de jour', _couleur: 'bg-green-100 border-green-400 text-green-800' },
  { id: 4, personnel_id: 4, type_garde_id: 1, date_debut: '2025-06-14T09:00:00', date_fin: '2025-06-14T17:00:00', statut: 'planifie', lieu: 'Cardiologie', observations: '', _nom: 'Dr. Sylla', _type: 'Garde de jour', _couleur: 'bg-amber-100 border-amber-400 text-amber-800' },
]

const jours = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const heures = ['07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00']

onMounted(async () => {
  await Promise.all([loadGardes(), loadPersonnel(), loadTypes()])
})

async function loadGardes() {
  loading.value = true
  try {
    const { data } = await gardesService.planning()
    gardes.value = Array.isArray(data) ? data : (data.results || DEMO_GARDES)
  } catch { gardes.value = DEMO_GARDES }
  finally { loading.value = false }
}

async function loadPersonnel() {
  try {
    const { data } = await personnelService.list()
    personnel.value = Array.isArray(data) ? data : []
  } catch { personnel.value = [] }
}

async function loadTypes() {
  try {
    const { data } = await gardesService.planning()
    typesGarde.value = Array.isArray(data) ? [] : []
  } catch { typesGarde.value = [{ id: 1, nom: 'Garde de jour' }, { id: 2, nom: 'Garde de nuit' }, { id: 3, nom: 'Astreinte' }] }
}

async function saveGarde() {
  saving.value = true
  try {
    const { data } = await gardesService.creer(form.value)
    gardes.value.push(data)
    toast.success('Garde planifiée avec succès')
    showModal.value = false
    resetForm()
  } catch {
    gardes.value.push({ id: Date.now(), ...form.value, statut: 'planifie', _nom: 'Nouveau', _type: 'Garde', _couleur: 'bg-gray-100 border-gray-400 text-gray-800' })
    toast.success('Garde planifiée (mode démo)')
    showModal.value = false
    resetForm()
  } finally { saving.value = false }
}

async function confirmerGarde(id) {
  try {
    await gardesService.confirmer(id)
    const g = gardes.value.find(x => x.id === id)
    if (g) g.statut = 'confirmé'
    toast.success('Garde confirmée')
  } catch { toast.error('Erreur lors de la confirmation') }
}

function resetForm() {
  form.value = { personnel_id: '', type_garde_id: '', date_debut: '', date_fin: '', lieu: '', observations: '' }
}

const statutColor = { 'confirmé': 'badge-success', 'planifie': 'badge-warning', 'annule': 'badge-danger', 'remplace': 'badge-violet' }

const gardesParJour = computed(() => {
  const result = {}
  jours.forEach(j => result[j] = [])
  gardes.value.forEach(g => {
    const d = new Date(g.date_debut)
    const jourIdx = (d.getDay() + 6) % 7 // Lundi = 0
    if (jourIdx < 7) result[jours[jourIdx]].push(g)
  })
  return result
})
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Planning de garde</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des gardes et astreintes du personnel</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Ajouter garde</button>
    </div>

    <!-- Stats rapides -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="stat-card p-4 text-center border-l-4 border-green-500">
        <p class="text-2xl font-extrabold text-green-600">{{ gardes.filter(g => g.statut === 'confirmé').length }}</p>
        <p class="text-xs text-gray-500">Gardes confirmées</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-amber-400">
        <p class="text-2xl font-extrabold text-amber-600">{{ gardes.filter(g => g.statut === 'planifie').length }}</p>
        <p class="text-xs text-gray-500">En attente</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-blue-500">
        <p class="text-2xl font-extrabold text-blue-600">{{ gardes.length }}</p>
        <p class="text-xs text-gray-500">Total semaine</p>
      </div>
      <div class="stat-card p-4 text-center border-l-4 border-violet-500">
        <p class="text-2xl font-extrabold text-violet-600">{{ new Set(gardes.map(g => g.personnel_id)).size }}</p>
        <p class="text-xs text-gray-500">Membres planifiés</p>
      </div>
    </div>

    <!-- Vue calendrier semaine -->
    <div class="stat-card p-5 overflow-x-auto">
      <p class="section-title mb-4">Vue calendrier — Semaine courante</p>
      <div class="grid grid-cols-8 gap-1 min-w-[700px]">
        <div class="text-xs text-gray-400 font-medium py-2"></div>
        <div v-for="j in jours" :key="j" class="text-center text-xs font-semibold text-violet-700 py-2 bg-violet-50 rounded-lg">{{ j }}</div>
        <template v-for="h in heures" :key="h">
          <div class="text-xs text-gray-400 py-3 pr-2 text-right">{{ h }}</div>
          <div v-for="j in jours" :key="j" class="border border-gray-100 rounded-lg min-h-[40px] bg-gray-50/50 relative">
            <div v-for="g in gardesParJour[j].filter(x => new Date(x.date_debut).getHours() === parseInt(h))" :key="g.id"
              :class="['absolute inset-0.5 rounded-md border-l-2 p-1 text-xs font-medium truncate cursor-pointer', g._couleur || 'bg-blue-100 border-blue-400 text-blue-800']">
              {{ g._nom || `Personnel #${g.personnel_id}` }}
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Liste des gardes -->
    <div class="stat-card overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex items-center justify-between">
        <p class="section-title">Gardes planifiées</p>
        <button @click="loadGardes" class="btn-secondary text-xs py-1.5">↻ Actualiser</button>
      </div>
      <div v-if="loading" class="flex justify-center py-8">
        <div class="w-6 h-6 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="g in gardes" :key="g.id" class="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors">
          <div :class="['w-1 h-12 rounded-full shrink-0', g.statut === 'confirmé' ? 'bg-green-500' : g.statut === 'annule' ? 'bg-red-500' : 'bg-amber-400']"></div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-gray-900 text-sm">{{ g._nom || `Personnel #${g.personnel_id}` }}</p>
            <p class="text-xs text-gray-500">{{ g._type || `Type #${g.type_garde_id}` }} · {{ g.lieu }}</p>
          </div>
          <div class="text-right text-xs text-gray-500">
            <p class="font-semibold">{{ new Date(g.date_debut).toLocaleDateString('fr-FR') }}</p>
            <p>{{ new Date(g.date_debut).toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit'}) }} – {{ new Date(g.date_fin).toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit'}) }}</p>
          </div>
          <span :class="['text-xs font-bold px-2.5 py-1 rounded-full shrink-0', statutColor[g.statut] || 'badge-info']">{{ g.statut }}</span>
          <button v-if="g.statut === 'planifie'" @click="confirmerGarde(g.id)" class="btn-success text-xs py-1 px-3">Confirmer</button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-bold text-gray-900 mb-5">Planifier une garde</h3>
          <form @submit.prevent="saveGarde" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="col-span-2">
                <label class="block text-xs font-medium text-gray-600 mb-1">Personnel *</label>
                <select v-model="form.personnel_id" class="input-field" required>
                  <option value="">Sélectionner...</option>
                  <option v-for="p in personnel" :key="p.id" :value="p.id">{{ p.full_name }} ({{ p.role }})</option>
                </select>
              </div>
              <div class="col-span-2">
                <label class="block text-xs font-medium text-gray-600 mb-1">Type de garde *</label>
                <select v-model="form.type_garde_id" class="input-field" required>
                  <option value="">Sélectionner...</option>
                  <option v-for="t in typesGarde" :key="t.id" :value="t.id">{{ t.nom }}</option>
                </select>
              </div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Début *</label><input v-model="form.date_debut" type="datetime-local" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Fin *</label><input v-model="form.date_fin" type="datetime-local" class="input-field" required /></div>
              <div class="col-span-2"><label class="block text-xs font-medium text-gray-600 mb-1">Lieu / Service</label><input v-model="form.lieu" class="input-field" placeholder="Ex: Urgences, Bloc A..." /></div>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1" :disabled="saving">
                <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block mr-2"></span>
                Planifier
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
