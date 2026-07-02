<script setup>
import { ref, computed } from 'vue'
import ChartComponent from '@/components/ChartComponent.vue'

const search = ref('')
const activeFilter = ref('Tous')

const accounts = ref([
  { id: 1, code: '401000', libelle: 'Fournisseurs', type: 'Passif', debit: 12500000, credit: 8500000, solde: 4000000 },
  { id: 2, code: '411000', libelle: 'Clients', type: 'Actif', debit: 18200000, credit: 5300000, solde: 12900000 },
  { id: 3, code: '512000', libelle: 'Banque', type: 'Actif', debit: 45000000, credit: 32000000, solde: 13000000 },
  { id: 4, code: '531000', libelle: 'Caisse', type: 'Actif', debit: 8500000, credit: 6200000, solde: 2300000 },
  { id: 5, code: '607000', libelle: 'Achats marchandises', type: 'Charge', debit: 32000000, credit: 0, solde: 32000000 },
  { id: 6, code: '701000', libelle: 'Ventes de services', type: 'Produit', debit: 0, credit: 28500000, solde: -28500000 },
])

const factures = ref([
  { id: 'F-2025-089', client: 'Diallo Mamadou', date: '2025-06-12', montant: 450000, tva: 90000, total: 540000, statut: 'Payée', delai: 0 },
  { id: 'F-2025-088', client: 'Koné Fatoumata', date: '2025-06-10', montant: 2800000, tva: 560000, total: 3360000, statut: 'Partielle', delai: 0 },
  { id: 'F-2025-087', client: 'Traoré Ibrahim', date: '2025-06-11', montant: 180000, tva: 36000, total: 216000, statut: 'En attente', delai: 15 },
  { id: 'F-2025-086', client: 'Bah Aissatou', date: '2025-06-09', montant: 95000, tva: 19000, total: 114000, statut: 'Payée', delai: 0 },
  { id: 'F-2025-085', client: 'Camara Sekou', date: '2025-06-08', montant: 320000, tva: 64000, total: 384000, statut: 'En attente', delai: 22 },
  { id: 'F-2025-084', client: 'Diallo Oumar', date: '2025-06-07', montant: 150000, tva: 30000, total: 180000, statut: 'Expirée', delai: 45 },
])

const depenses = ref([
  { id: 1, date: '2025-06-12', categorie: 'Achats médicaments', montant: 1250000, fournisseur: 'PharmaGuinée', justificatif: true },
  { id: 2, date: '2025-06-11', categorie: 'Salaires', montant: 8500000, fournisseur: 'Personnel', justificatif: true },
  { id: 3, date: '2025-06-10', categorie: 'Maintenance', montant: 750000, fournisseur: 'TechSolutions', justificatif: true },
  { id: 4, date: '2025-06-09', categorie: 'Électricité', montant: 320000, fournisseur: 'SEEG', justificatif: true },
  { id: 5, date: '2025-06-08', categorie: 'Achats matériel médical', montant: 2100000, fournisseur: 'MedEquip', justificatif: false },
])

const filters = ['Tous', 'Payée', 'Partielle', 'En attente', 'Expirée']

const filteredFactures = computed(() =>
  factures.value.filter(f =>
    (activeFilter.value === 'Tous' || f.statut === activeFilter.value) &&
    f.client.toLowerCase().includes(search.value.toLowerCase())
  )
)

const stats = computed(() => {
  const totalRecettes = factures.value.reduce((s, f) => s + f.total, 0)
  const totalDepenses = depenses.value.reduce((s, d) => s + d.montant, 0)
  const totalPaye = factures.value.reduce((s, f) => s + (f.statut === 'Payée' ? f.total : f.statut === 'Partielle' ? f.montant : 0), 0)
  const enAttente = factures.value.filter(f => f.statut === 'En attente').reduce((s, f) => s + f.total, 0)
  expiree = factures.value.filter(f => f.statut === 'Expirée').reduce((s, f) => s + f.total, 0)
  const benefice = totalRecettes - totalDepenses
  return { totalRecettes, totalDepenses, totalPaye, enAttente, expiree, benefice }
})

const statutColor = {
  'Payée': 'badge-success',
  'Partielle': 'badge-warning',
  'En attente': 'badge-danger',
  'Expirée': 'badge-danger'
}

function fmt(n) {
  return n.toLocaleString('fr-FR') + ' GNF'
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function exportCSV() {
  const headers = 'ID,Client,Date,Montant,TVA,Total,Statut,Délai\n'
  const rows = factures.value.map(f =>
    `${f.id},${f.client},${f.date},${f.montant},${f.tva},${f.total},${f.statut},${f.delai}`
  ).join('\n')
  const csv = headers + rows
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `comptabilite_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  alert('📥 Export CSV téléchargé avec succès !')
}

function generateRapport() {
  alert(`📊 Rapport comptable généré !\n\nTotal recettes: ${fmt(stats.value.totalRecettes)}\nTotal dépenses: ${fmt(stats.value.totalDepenses)}\nBénéfice: ${fmt(stats.value.benefice)}`)
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h2 class="page-title">Comptabilité</h2>
        <p class="text-sm text-violet-500 mt-0.5">Gestion financière, factures, dépenses et rapports</p>
      </div>
      <div class="flex gap-2">
        <button type="button" class="btn-secondary" @click="exportCSV">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Exporter CSV
        </button>
        <button type="button" class="btn-primary" @click="generateRapport">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Générer rapport
        </button>
      </div>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="stat-card p-5 card-hover">
        <div class="flex items-center gap-3 mb-3">
          <div class="kpi-icon bg-gradient-to-br from-green-100 to-emerald-100">💰</div>
          <p class="text-xs font-semibold text-gray-500 uppercase">Recettes</p>
        </div>
        <p class="text-xl font-extrabold text-gray-900">{{ fmt(stats.totalRecettes) }}</p>
        <p class="text-xs text-green-600 mt-1 font-semibold">↑ 12% ce mois</p>
      </div>
      <div class="stat-card p-5 card-hover">
        <div class="flex items-center gap-3 mb-3">
          <div class="kpi-icon bg-gradient-to-br from-red-100 to-rose-100">💸</div>
          <p class="text-xs font-semibold text-gray-500 uppercase">Dépenses</p>
        </div>
        <p class="text-xl font-extrabold text-gray-900">{{ fmt(stats.totalDepenses) }}</p>
        <p class="text-xs text-red-600 mt-1 font-semibold">↑ 8% ce mois</p>
      </div>
      <div class="stat-card p-5 card-hover">
        <div class="flex items-center gap-3 mb-3">
          <div class="kpi-icon bg-gradient-to-br from-blue-100 to-violet-100">📈</div>
          <p class="text-xs font-semibold text-gray-500 uppercase">Bénéfice</p>
        </div>
        <p class="text-xl font-extrabold" :class="stats.benefice >= 0 ? 'text-green-600' : 'text-red-600'">
          {{ fmt(stats.benefice) }}
        </p>
        <p class="text-xs text-gray-500 mt-1">Marge: {{ ((stats.benefice / stats.totalRecettes) * 100).toFixed(1) }}%</p>
      </div>
      <div class="stat-card p-5 card-hover">
        <div class="flex items-center gap-3 mb-3">
          <div class="kpi-icon bg-gradient-to-br from-amber-100 to-orange-100">⏳</div>
          <p class="text-xs font-semibold text-gray-500 uppercase">En attente</p>
        </div>
        <p class="text-xl font-extrabold text-amber-600">{{ fmt(stats.enAttente) }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ factures.filter(f => f.statut === 'En attente').length }} factures</p>
      </div>
      <div class="stat-card p-5 card-hover">
        <div class="flex items-center gap-3 mb-3">
          <div class="kpi-icon bg-gradient-to-br from-red-100 to-rose-100">⚠️</div>
          <p class="text-xs font-semibold text-gray-500 uppercase">Expirées</p>
        </div>
        <p class="text-xl font-extrabold text-red-600">{{ fmt(stats.expiree) }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ factures.filter(f => f.statut === 'Expirée').length }} factures</p>
      </div>
    </div>

    <!-- Graphiques -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <ChartComponent
        type="bar"
        :data="[450, 336, 216, 114, 384, 180]"
        :labels="['Jun 08', 'Jun 09', 'Jun 10', 'Jun 11', 'Jun 12', 'Auj.']"
        title="Factures émises (milliers GNF)"
        :colors="['#7c3aed', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']"
      />
      <ChartComponent
        type="line"
        :data="[1250, 850, 75, 32, 210]"
        :labels="['Médicaments', 'Salaires', 'Maintenance', 'Électricité', 'Matériel']"
        title="Répartition des dépenses par catégorie"
        :colors="['#7c3aed', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']"
      />
    </div>

    <!-- Filtres + recherche -->
    <div class="stat-card p-4 flex flex-wrap gap-3 items-center">
      <input v-model="search" class="input-field max-w-xs" placeholder="🔍 Rechercher un client..." />
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="f in filters" :key="f"
          @click="activeFilter = f"
          :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all', activeFilter === f ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-md' : 'bg-violet-50 text-violet-700 hover:bg-violet-100']"
        >
          {{ f }}
        </button>
      </div>
    </div>

    <!-- Tableau des factures -->
    <div class="stat-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">N° Facture</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Client</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Montant HT</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">TVA (20%)</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Total TTC</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Délai</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in filteredFactures" :key="f.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-mono text-xs text-violet-700 font-semibold">{{ f.id }}</td>
              <td class="px-4 py-3 font-medium text-gray-900">{{ f.client }}</td>
              <td class="px-4 py-3 text-gray-500">{{ formatDate(f.date) }}</td>
              <td class="px-4 py-3 font-semibold text-gray-900">{{ fmt(f.montant) }}</td>
              <td class="px-4 py-3 text-gray-500">{{ fmt(f.tva) }}</td>
              <td class="px-4 py-3 font-bold text-gray-900">{{ fmt(f.total) }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full', statutColor[f.statut]]">{{ f.statut }}</span>
              </td>
              <td class="px-4 py-3">
                <span v-if="f.delai > 0" :class="['text-xs font-bold px-2.5 py-1 rounded-full', f.delai > 30 ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700']">
                  {{ f.delai }}j
                </span>
                <span v-else class="text-xs text-green-600 font-semibold">✓</span>
              </td>
              <td class="px-4 py-3">
                <button type="button" class="text-violet-600 hover:text-violet-800 text-xs font-medium mr-2" @click="alert('📄 Voir facture ' + f.id)">PDF</button>
                <button type="button" class="text-blue-600 hover:text-blue-800 text-xs font-medium" @click="alert('✉️ Envoyer rappel à ' + f.client)">Rappel</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tableau des dépenses -->
    <div class="stat-card overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <h3 class="font-bold text-gray-900">📊 Dernières dépenses</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Catégorie</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Fournisseur</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Montant</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Justificatif</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in depenses" :key="d.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 text-gray-500">{{ formatDate(d.date) }}</td>
              <td class="px-4 py-3 font-medium text-gray-900">{{ d.categorie }}</td>
              <td class="px-4 py-3 text-gray-500">{{ d.fournisseur }}</td>
              <td class="px-4 py-3 font-bold text-red-600">{{ fmt(d.montant) }}</td>
              <td class="px-4 py-3">
                <span v-if="d.justificatif" class="text-green-600 text-xs font-semibold">✅ Oui</span>
                <span v-else class="text-amber-600 text-xs font-semibold">⚠️ Non</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Plans comptables -->
    <div class="stat-card overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <h3 class="font-bold text-gray-900">📋 Plans comptables</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Code</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Libellé</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Type</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Débit</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Crédit</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Solde</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in accounts" :key="a.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 font-mono text-xs font-semibold text-violet-700">{{ a.code }}</td>
              <td class="px-4 py-3 font-medium text-gray-900">{{ a.libelle }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-medium px-2.5 py-1 rounded-full',
                  a.type === 'Actif' ? 'badge-info' :
                  a.type === 'Passif' ? 'badge-warning' :
                  a.type === 'Charge' ? 'badge-danger' : 'badge-success']">
                  {{ a.type }}
                </span>
              </td>
              <td class="px-4 py-3 font-semibold text-green-700">{{ a.debit > 0 ? fmt(a.debit) : '-' }}</td>
              <td class="px-4 py-3 font-semibold text-blue-700">{{ a.credit > 0 ? fmt(a.credit) : '-' }}</td>
              <td class="px-4 py-3 font-bold" :class="a.solde >= 0 ? 'text-green-700' : 'text-red-700'">
                {{ fmt(Math.abs(a.solde)) }} {{ a.solde < 0 ? '(crédit)' : '(débit)' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
