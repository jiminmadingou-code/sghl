<script setup>
import { ref, computed } from 'vue'
import { downloadOrdonnancePDF } from '@/services/pdf'

const ordonnances = ref([
  {
    id: 1, date: '2025-06-10', medecin: 'Dr. Camara Alpha', service: 'Médecine interne',
    valide_jusqu: '2025-09-10', statut: 'Valide',
    medicaments: [
      { nom: 'Artémether 80mg', posologie: '1 comprimé matin et soir', duree: '3 jours', qte: 6 },
      { nom: 'Paracétamol 500mg', posologie: '1 comprimé toutes les 6h si douleur', duree: '5 jours', qte: 20 },
    ]
  },
  {
    id: 2, date: '2025-05-20', medecin: 'Dr. Bah Mariama', service: 'Cardiologie',
    valide_jusqu: '2025-08-20', statut: 'Valide',
    medicaments: [
      { nom: 'Amlodipine 5mg', posologie: '1 comprimé le matin', duree: '3 mois', qte: 90 },
    ]
  },
  {
    id: 3, date: '2025-02-15', medecin: 'Dr. Camara Alpha', service: 'Médecine interne',
    valide_jusqu: '2025-05-15', statut: 'Expirée',
    medicaments: [
      { nom: 'Metformine 500mg', posologie: '1 comprimé matin et soir', duree: '3 mois', qte: 180 },
    ]
  },
])

const filtered = computed(() => ordonnances.value)

function joursRestants(date) {
  const diff = new Date(date) - new Date()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}
function telechargerPDF(o) { downloadOrdonnancePDF(o) }
</script>

<template>
  <div class="space-y-5">
    <div>
      <h1 class="text-2xl font-extrabold text-gray-900">Mes ordonnances</h1>
      <p class="text-sm text-gray-500 mt-0.5">Consultez et téléchargez vos prescriptions médicales</p>
    </div>

    <!-- Alerte ordonnance expirée -->
    <div v-if="ordonnances.some(o => o.statut === 'Expirée')" class="alert-warning-banner flex items-center gap-3">
      <span class="text-amber-700 font-bold text-sm">⚠</span>
      <p class="text-sm text-amber-800">
        <strong>{{ ordonnances.filter(o => o.statut === 'Expirée').length }} ordonnance(s) expirée(s).</strong>
        Consultez votre médecin pour un renouvellement.
      </p>
    </div>

    <div class="space-y-4">
      <div v-for="o in filtered" :key="o.id"
        :class="['bg-white rounded-2xl border-2 overflow-hidden', o.statut === 'Expirée' ? 'border-gray-200 opacity-75' : 'border-violet-200']">

        <!-- Header -->
        <div :class="['px-5 py-4 flex items-start justify-between gap-4 flex-wrap', o.statut === 'Expirée' ? 'bg-gray-50' : 'bg-violet-50']">
          <div class="flex items-center gap-3">
            <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-white text-xl shrink-0', o.statut === 'Expirée' ? 'bg-gray-400' : 'bg-violet-600']">
              💊
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <p class="font-bold text-gray-900">Ordonnance du {{ o.date }}</p>
                <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', o.statut === 'Valide' ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600']">
                  {{ o.statut }}
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-0.5">{{ o.medecin }} · {{ o.service }}</p>
              <p class="text-xs mt-1" :class="o.statut === 'Expirée' ? 'text-red-500 font-semibold' : joursRestants(o.valide_jusqu) <= 30 ? 'text-amber-600 font-semibold' : 'text-gray-400'">
                {{ o.statut === 'Expirée' ? '⚠ Expirée le ' + o.valide_jusqu : 'Valide jusqu\'au ' + o.valide_jusqu + (joursRestants(o.valide_jusqu) <= 30 ? ' (' + joursRestants(o.valide_jusqu) + ' jours)' : '') }}
              </p>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="telechargerPDF(o)" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-violet-600 text-white text-xs font-semibold hover:bg-violet-700 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Télécharger PDF
            </button>
            <button v-if="o.statut === 'Expirée'" class="px-3 py-1.5 rounded-xl border border-violet-300 text-violet-700 text-xs font-semibold hover:bg-violet-50 transition-colors">
              Demander renouvellement
            </button>
          </div>
        </div>

        <!-- Médicaments -->
        <div class="px-5 py-4">
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Médicaments prescrits</p>
          <div class="space-y-3">
            <div v-for="m in o.medicaments" :key="m.nom"
              class="flex items-start gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100">
              <div class="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center text-sm shrink-0">💊</div>
              <div class="flex-1">
                <p class="font-bold text-gray-900 text-sm">{{ m.nom }}</p>
                <p class="text-xs text-gray-600 mt-0.5">{{ m.posologie }}</p>
                <div class="flex gap-3 mt-1">
                  <span class="text-[10px] bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full font-semibold">Durée : {{ m.duree }}</span>
                  <span class="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-semibold">Qté : {{ m.qte }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
