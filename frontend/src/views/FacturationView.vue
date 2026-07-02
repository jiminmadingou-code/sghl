<script setup>
import { ref, computed, reactive } from 'vue'

const search = ref('')
const showModal = ref(false)

const newFacture = reactive({ patient: '', type: 'Consultation', montant: '' })

const typesFacture = ['Consultation', 'Hospitalisation', 'Examens', 'Pharmacie', 'Chirurgie', 'Maternité']

function ajouterFacture() {
  if (!newFacture.patient || !newFacture.montant) return
  const id = `F-2025-${String(factures.value.length + 1).padStart(3, '0')}`
  factures.value.unshift({
    id, patient: newFacture.patient, date: new Date().toISOString().slice(0,10),
    montant: Number(newFacture.montant), paye: 0, statut: 'En attente', type: newFacture.type,
  })
  Object.assign(newFacture, { patient: '', type: 'Consultation', montant: '' })
  showModal.value = false
}

const factures = ref([
  { id: 'F-2025-001', patient: 'Diallo Mamadou', date: '2025-06-12', montant: 450000, paye: 450000, statut: 'Payée', type: 'Consultation' },
  { id: 'F-2025-002', patient: 'Koné Fatoumata', date: '2025-06-10', montant: 2800000, paye: 1400000, statut: 'Partielle', type: 'Hospitalisation' },
  { id: 'F-2025-003', patient: 'Traoré Ibrahim', date: '2025-06-11', montant: 180000, paye: 0, statut: 'En attente', type: 'Examens' },
  { id: 'F-2025-004', patient: 'Bah Aissatou', date: '2025-06-09', montant: 95000, paye: 95000, statut: 'Payée', type: 'Pharmacie' },
  { id: 'F-2025-005', patient: 'Camara Sekou', date: '2025-06-08', montant: 320000, paye: 0, statut: 'En attente', type: 'Consultation' },
])

const filtered = computed(() =>
  factures.value.filter(f => f.patient.toLowerCase().includes(search.value.toLowerCase()))
)

const totalRecettes = computed(() => factures.value.reduce((s, f) => s + f.paye, 0))
const totalAttente = computed(() => factures.value.reduce((s, f) => s + (f.montant - f.paye), 0))

const statutColor = { 'Payée': 'badge-success', 'Partielle': 'badge-warning', 'En attente': 'badge-danger' }

function fmt(n) { return n.toLocaleString('fr-FR') + ' GNF' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Facturation</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestion des factures et paiements</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Nouvelle facture</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="stat-card p-5 card-hover">
        <div class="kpi-icon bg-green-100 mb-2">💰</div>
        <p class="text-xl font-bold text-gray-900">{{ fmt(totalRecettes) }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Recettes encaissées</p>
      </div>
      <div class="stat-card p-5 card-hover">
        <div class="kpi-icon bg-amber-100 mb-2">⏳</div>
        <p class="text-xl font-bold text-gray-900">{{ fmt(totalAttente) }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Montants en attente</p>
      </div>
      <div class="stat-card p-5 card-hover">
        <div class="kpi-icon bg-violet-100 mb-2">📄</div>
        <p class="text-xl font-bold text-gray-900">{{ factures.length }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Factures émises</p>
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
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">N° Facture</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Patient</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Type</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Montant</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Payé</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in filtered" :key="f.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-mono text-xs text-violet-700 font-semibold">{{ f.id }}</td>
              <td class="px-4 py-3 font-medium text-gray-900">{{ f.patient }}</td>
              <td class="px-4 py-3 text-gray-500">{{ f.date }}</td>
              <td class="px-4 py-3"><span class="badge-info text-xs px-2.5 py-1 rounded-full font-medium">{{ f.type }}</span></td>
              <td class="px-4 py-3 font-semibold text-gray-900">{{ fmt(f.montant) }}</td>
              <td class="px-4 py-3 text-green-700 font-semibold">{{ fmt(f.paye) }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[f.statut]]">{{ f.statut }}</span>
              </td>
              <td class="px-4 py-3">
                <button class="text-violet-600 hover:text-violet-800 text-xs font-medium">PDF</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3 class="text-lg font-bold text-gray-900 mb-4">📋 Nouvelle facture</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Patient *</label>
            <input v-model="newFacture.patient" class="input-field" placeholder="Nom du patient" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Type de prestation</label>
              <select v-model="newFacture.type" class="input-field">
                <option v-for="t in typesFacture" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Montant (GNF) *</label>
              <input v-model="newFacture.montant" type="number" class="input-field" placeholder="450000" />
            </div>
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterFacture" class="btn-primary flex-1">✅ Émettre la facture</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
