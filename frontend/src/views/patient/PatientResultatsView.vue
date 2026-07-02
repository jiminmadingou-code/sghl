<script setup>
import { ref, computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import { downloadResultatPDF } from '@/services/pdf'

const toast = useToastStore()
const search = ref('')
const activeFilter = ref('Tous')

const resultats = ref([
  { id: 1, date: '2025-06-10', type: 'NFS',           prescripteur: 'Dr. Camara',  biologiste: 'Dr. Diallo', statut: 'Disponible', nouveau: true,
    valeurs: [{ nom: 'Hémoglobine', val: '11.2', unite: 'g/dL', ref: '12–16', alerte: true }, { nom: 'Globules blancs', val: '8500', unite: '/mm³', ref: '4000–10000', alerte: false }, { nom: 'Plaquettes', val: '210000', unite: '/mm³', ref: '150000–400000', alerte: false }] },
  { id: 2, date: '2025-06-10', type: 'Glycémie',      prescripteur: 'Dr. Camara',  biologiste: 'Dr. Diallo', statut: 'Disponible', nouveau: true,
    valeurs: [{ nom: 'Glycémie à jeun', val: '1.42', unite: 'g/L', ref: '0.70–1.10', alerte: true }] },
  { id: 3, date: '2025-05-20', type: 'ECG',           prescripteur: 'Dr. Bah',     biologiste: 'Dr. Sylla',  statut: 'Disponible', nouveau: false,
    valeurs: [{ nom: 'Rythme', val: 'Sinusal normal', unite: '', ref: 'Normal', alerte: false }] },
  { id: 4, date: '2025-04-15', type: 'Radiographie',  prescripteur: 'Dr. Camara',  biologiste: 'Dr. Sylla',  statut: 'Disponible', nouveau: false,
    valeurs: [{ nom: 'Compte-rendu', val: 'Pas d\'anomalie visible', unite: '', ref: 'Normal', alerte: false }] },
  { id: 5, date: '2025-03-08', type: 'Bilan lipidique',prescripteur: 'Dr. Bah',    biologiste: 'Dr. Diallo', statut: 'Disponible', nouveau: false,
    valeurs: [{ nom: 'Cholestérol total', val: '2.1', unite: 'g/L', ref: '< 2.0', alerte: true }, { nom: 'HDL', val: '0.55', unite: 'g/L', ref: '> 0.40', alerte: false }] },
])

const filters = ['Tous', 'Nouveaux', 'Biologie', 'Imagerie']
const expanded = ref(null)

const filtered = computed(() => resultats.value.filter(r => {
  const matchSearch = r.type.toLowerCase().includes(search.value.toLowerCase())
  const matchFilter = activeFilter.value === 'Tous' ||
    (activeFilter.value === 'Nouveaux' && r.nouveau) ||
    (activeFilter.value === 'Biologie' && ['NFS','Glycémie','Bilan lipidique'].includes(r.type)) ||
    (activeFilter.value === 'Imagerie' && ['Radiographie','ECG'].includes(r.type))
  return matchSearch && matchFilter
}))

function toggleExpand(id) { expanded.value = expanded.value === id ? null : id }
function telechargerPDF(r) { downloadResultatPDF(r) }
function telechargerDICOM(r) { toast.info(`Fichier DICOM "${r.type}" en cours de téléchargement...`) }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Mes résultats d'examens</h1>
        <p class="text-sm text-gray-500 mt-0.5">Consultez et téléchargez vos comptes-rendus médicaux</p>
      </div>
      <div class="flex items-center gap-2 bg-teal-50 border border-teal-200 rounded-xl px-3 py-2">
        <span class="w-2 h-2 rounded-full bg-teal-500"></span>
        <span class="text-xs font-semibold text-teal-700">{{ resultats.filter(r => r.nouveau).length }} nouveau(x)</span>
      </div>
    </div>

    <!-- Filtres -->
    <div class="bg-white rounded-2xl border border-gray-100 p-4 flex flex-wrap gap-3 items-center">
      <input v-model="search" class="input-field max-w-xs" placeholder="🔍 Rechercher un examen..." />
      <div class="flex gap-2 flex-wrap">
        <button v-for="f in filters" :key="f" @click="activeFilter = f"
          :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition-all',
            activeFilter === f ? 'bg-teal-600 text-white' : 'bg-teal-50 text-teal-700 hover:bg-teal-100']">
          {{ f }}
        </button>
      </div>
    </div>

    <!-- Liste résultats -->
    <div class="space-y-3">
      <div v-for="r in filtered" :key="r.id" class="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:border-teal-200 transition-colors">

        <!-- Header résultat -->
        <div class="flex items-center gap-4 p-4 cursor-pointer" @click="toggleExpand(r.id)">
          <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-white text-xl shrink-0', r.nouveau ? 'bg-teal-600' : 'bg-gray-400']">
            🔬
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="font-bold text-gray-900">{{ r.type }}</p>
              <span v-if="r.nouveau" class="text-[10px] font-bold bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">NOUVEAU</span>
              <span v-if="r.valeurs.some(v => v.alerte)" class="text-[10px] font-bold bg-red-100 text-red-700 px-2 py-0.5 rounded-full">⚠ Valeur anormale</span>
            </div>
            <p class="text-xs text-gray-500 mt-0.5">{{ r.date }} · Prescrit par {{ r.prescripteur }} · Validé par {{ r.biologiste }}</p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button @click.stop="telechargerPDF(r)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-600 text-white text-xs font-semibold hover:bg-teal-700 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              PDF
            </button>
            <svg :class="['w-4 h-4 text-gray-400 transition-transform', expanded === r.id ? 'rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>

        <!-- Détail valeurs -->
        <div v-if="expanded === r.id" class="border-t border-gray-100 px-4 pb-4 pt-3 bg-gray-50">
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Résultats détaillés</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div v-for="v in r.valeurs" :key="v.nom"
              :class="['p-3 rounded-xl border', v.alerte ? 'bg-red-50 border-red-200' : 'bg-white border-gray-100']">
              <p class="text-xs text-gray-500 mb-1">{{ v.nom }}</p>
              <p :class="['text-lg font-extrabold', v.alerte ? 'text-red-600' : 'text-gray-900']">
                {{ v.val }} <span class="text-xs font-normal text-gray-400">{{ v.unite }}</span>
              </p>
              <p class="text-[10px] text-gray-400 mt-0.5">Référence : {{ v.ref }}</p>
              <span v-if="v.alerte" class="text-[10px] font-bold text-red-600">⚠ Hors norme</span>
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-3 italic">
            Ces résultats ont été validés par {{ r.biologiste }}. Consultez votre médecin pour toute interprétation.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
