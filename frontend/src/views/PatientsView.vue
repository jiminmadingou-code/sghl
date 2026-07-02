<script setup>
import { ref, computed, onMounted } from 'vue'
import { patientsService } from '@/services/sghl'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const search = ref('')
const showModal = ref(false)
const loading = ref(true)
const saving = ref(false)
const filterStatut = ref('')

const patients = ref([])
const form = ref({ nom: '', prenom: '', date_naissance: '', sexe: 'M', telephone: '', adresse: '', groupe_sanguin: '', allergies: '', antecedents: '' })

const DEMO = [
  { id: 1, nom: 'Diallo',  prenom: 'Mamadou',   date_naissance: '1979-03-15', sexe: 'M', telephone: '620 00 00 01', groupe_sanguin: 'A+', statut: 'Hospitalisé' },
  { id: 2, nom: 'Koné',    prenom: 'Fatoumata',  date_naissance: '1992-07-22', sexe: 'F', telephone: '621 00 00 02', groupe_sanguin: 'O+', statut: 'Actif' },
  { id: 3, nom: 'Traoré',  prenom: 'Ibrahim',    date_naissance: '1957-11-08', sexe: 'M', telephone: '622 00 00 03', groupe_sanguin: 'B-', statut: 'Actif' },
  { id: 4, nom: 'Bah',     prenom: 'Aissatou',   date_naissance: '1996-01-30', sexe: 'F', telephone: '623 00 00 04', groupe_sanguin: 'AB+', statut: 'Sorti' },
  { id: 5, nom: 'Camara',  prenom: 'Sekou',      date_naissance: '1970-05-12', sexe: 'M', telephone: '624 00 00 05', groupe_sanguin: 'O-', statut: 'Actif' },
  { id: 6, nom: 'Sylla',   prenom: 'Oumou',      date_naissance: '1988-09-03', sexe: 'F', telephone: '625 00 00 06', groupe_sanguin: 'A-', statut: 'Actif' },
]

onMounted(load)

async function load() {
  loading.value = true
  try {
    const { data } = await patientsService.list(search.value)
    patients.value = Array.isArray(data) ? data : (data.results || DEMO)
  } catch {
    patients.value = DEMO
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  let list = patients.value
  if (search.value) list = list.filter(p => `${p.nom} ${p.prenom}`.toLowerCase().includes(search.value.toLowerCase()))
  if (filterStatut.value) list = list.filter(p => p.statut === filterStatut.value)
  return list
})

function age(ddn) { return new Date().getFullYear() - new Date(ddn).getFullYear() }

async function addPatient() {
  saving.value = true
  try {
    const { data } = await patientsService.create(form.value)
    patients.value.unshift(data)
    toast.success('Patient enregistré avec succès')
    showModal.value = false
    resetForm()
  } catch {
    // Mode démo : ajout local
    patients.value.unshift({ id: Date.now(), ...form.value, statut: 'Actif' })
    toast.success('Patient enregistré (mode démo)')
    showModal.value = false
    resetForm()
  } finally {
    saving.value = false
  }
}

function resetForm() {
  form.value = { nom: '', prenom: '', date_naissance: '', sexe: 'M', telephone: '', adresse: '', groupe_sanguin: '', allergies: '', antecedents: '' }
}

const statutColor = { 'Actif': 'badge-success', 'Hospitalisé': 'badge-info', 'Sorti': 'badge-violet' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h2 class="page-title">Patients</h2>
        <p class="text-sm text-gray-500 mt-0.5">{{ filtered.length }} patient(s) enregistré(s)</p>
      </div>
      <button @click="showModal = true" class="btn-primary flex items-center gap-2"><span>+</span> Nouveau patient</button>
    </div>

    <div class="stat-card p-4 flex flex-col sm:flex-row gap-3">
      <input v-model="search" @input="load" type="text" class="input-field sm:max-w-xs" placeholder="🔍  Rechercher un patient..." />
      <select v-model="filterStatut" class="input-field sm:max-w-[160px]">
        <option value="">Tous les statuts</option>
        <option>Actif</option><option>Hospitalisé</option><option>Sorti</option>
      </select>
      <button @click="load" class="btn-secondary">↻ Actualiser</button>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Patient</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Âge / Sexe</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Téléphone</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Groupe sanguin</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full bg-violet-100 flex items-center justify-center text-violet-700 font-bold text-sm">
                    {{ (p.prenom?.[0] || '') }}{{ (p.nom?.[0] || '') }}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ p.prenom }} {{ p.nom }}</p>
                    <p class="text-xs text-gray-400">ID-{{ String(p.id).padStart(5, '0') }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ age(p.date_naissance) }} ans · {{ p.sexe === 'M' ? '♂' : '♀' }}</td>
              <td class="px-4 py-3 text-gray-600">{{ p.telephone }}</td>
              <td class="px-4 py-3">
                <span class="badge-violet text-xs font-semibold px-2.5 py-1 rounded-full">{{ p.groupe_sanguin }}</span>
              </td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[p.statut] || 'badge-info']">{{ p.statut }}</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-2">
                  <RouterLink :to="`/dashboard/patients/${p.id}`" class="text-violet-600 hover:text-violet-800 text-xs font-medium">Voir</RouterLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-bold text-gray-900 mb-5">Nouveau patient</h3>
          <form @submit.prevent="addPatient" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Prénom *</label><input v-model="form.prenom" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Nom *</label><input v-model="form.nom" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Date de naissance *</label><input v-model="form.date_naissance" type="date" class="input-field" required /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Sexe</label>
                <select v-model="form.sexe" class="input-field"><option value="M">Masculin</option><option value="F">Féminin</option></select>
              </div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Téléphone</label><input v-model="form.telephone" class="input-field" /></div>
              <div><label class="block text-xs font-medium text-gray-600 mb-1">Groupe sanguin</label>
                <select v-model="form.groupe_sanguin" class="input-field">
                  <option value="">—</option>
                  <option v-for="g in ['A+','A-','B+','B-','AB+','AB-','O+','O-']" :key="g">{{ g }}</option>
                </select>
              </div>
            </div>
            <div><label class="block text-xs font-medium text-gray-600 mb-1">Adresse</label><input v-model="form.adresse" class="input-field" /></div>
            <div><label class="block text-xs font-medium text-gray-600 mb-1">Allergies connues</label><input v-model="form.allergies" class="input-field" placeholder="Ex: Pénicilline, Aspirine..." /></div>
            <div><label class="block text-xs font-medium text-gray-600 mb-1">Antécédents médicaux</label><textarea v-model="form.antecedents" class="input-field" rows="2" placeholder="HTA, Diabète..."></textarea></div>
            <div class="flex gap-3 pt-2">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1" :disabled="saving">
                <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block mr-2"></span>
                Enregistrer
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
