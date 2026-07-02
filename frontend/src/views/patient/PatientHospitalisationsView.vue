<script setup>
import { ref } from 'vue'

const hospitalisations = ref([
  {
    id: 1, statut: 'En cours',
    service: 'Médecine interne', chambre: 'C-12', lit: 'L-02',
    medecin: 'Dr. Camara Alpha', entree: '2025-06-08', sortie_prev: '2025-06-18',
    motif: 'Paludisme sévère avec complications',
    soins: ['Artémether IV', 'Perfusion hydratation', 'Surveillance constantes toutes les 4h'],
    documents: [
      { nom: 'Compte-rendu d\'hospitalisation', date: '2025-06-08', type: 'PDF' },
      { nom: 'Résultats NFS à l\'entrée', date: '2025-06-08', type: 'PDF' },
    ]
  },
  {
    id: 2, statut: 'Terminé',
    service: 'Chirurgie générale', chambre: 'B-05', lit: 'L-01',
    medecin: 'Dr. Sylla Kadiatou', entree: '2024-11-10', sortie_prev: '2024-11-15', sortie_reelle: '2024-11-14',
    motif: 'Appendicectomie laparoscopique',
    soins: ['Anesthésie générale', 'Intervention chirurgicale', 'Soins post-opératoires'],
    documents: [
      { nom: 'Compte-rendu opératoire', date: '2024-11-10', type: 'PDF' },
      { nom: 'Ordonnance de sortie', date: '2024-11-14', type: 'PDF' },
      { nom: 'Certificat médical', date: '2024-11-14', type: 'PDF' },
    ]
  },
])

function duree(entree, sortie) {
  const diff = new Date(sortie || new Date()) - new Date(entree)
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

const expanded = ref(1)
</script>

<template>
  <div class="space-y-5">
    <div>
      <h1 class="text-2xl font-extrabold text-gray-900">Mes hospitalisations</h1>
      <p class="text-sm text-gray-500 mt-0.5">Historique de vos séjours hospitaliers et documents associés</p>
    </div>

    <!-- Hospitalisation en cours -->
    <div v-if="hospitalisations.some(h => h.statut === 'En cours')" class="alert-info-banner flex items-center gap-3">
      <span class="text-blue-700 font-bold">🏥</span>
      <p class="text-sm text-blue-800">
        Vous êtes actuellement hospitalisé(e) en <strong>{{ hospitalisations.find(h => h.statut === 'En cours')?.service }}</strong>.
        Sortie prévue le <strong>{{ hospitalisations.find(h => h.statut === 'En cours')?.sortie_prev }}</strong>.
      </p>
    </div>

    <div class="space-y-4">
      <div v-for="h in hospitalisations" :key="h.id"
        :class="['bg-white rounded-2xl border-2 overflow-hidden', h.statut === 'En cours' ? 'border-blue-300' : 'border-gray-100']">

        <!-- Header -->
        <div :class="['px-5 py-4 cursor-pointer', h.statut === 'En cours' ? 'bg-blue-50' : 'bg-gray-50']"
          @click="expanded = expanded === h.id ? null : h.id">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div class="flex items-center gap-4">
              <div :class="['w-14 h-14 rounded-2xl flex flex-col items-center justify-center text-white shrink-0', h.statut === 'En cours' ? 'bg-blue-600' : 'bg-gray-500']">
                <span class="text-xl">🏥</span>
              </div>
              <div>
                <div class="flex items-center gap-2 flex-wrap mb-1">
                  <p class="font-extrabold text-gray-900">{{ h.service }}</p>
                  <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', h.statut === 'En cours' ? 'bg-blue-100 text-blue-700' : 'bg-gray-200 text-gray-600']">
                    {{ h.statut }}
                  </span>
                </div>
                <p class="text-sm text-gray-600">{{ h.motif }}</p>
                <div class="flex flex-wrap gap-3 mt-1 text-xs text-gray-500">
                  <span>📅 Entrée : {{ h.entree }}</span>
                  <span>📅 Sortie {{ h.statut === 'En cours' ? 'prévue' : 'réelle' }} : {{ h.sortie_reelle || h.sortie_prev }}</span>
                  <span>⏱ {{ duree(h.entree, h.sortie_reelle || h.sortie_prev) }} jour(s)</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <div class="text-right hidden sm:block">
                <p class="text-xs text-gray-500">Chambre / Lit</p>
                <p class="font-bold text-violet-700 text-sm">{{ h.chambre }} · {{ h.lit }}</p>
              </div>
              <svg :class="['w-5 h-5 text-gray-400 transition-transform', expanded === h.id ? 'rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Détail -->
        <div v-if="expanded === h.id" class="px-5 pb-5 pt-4 space-y-4">

          <!-- Infos -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="bg-gray-50 rounded-xl p-3">
              <p class="text-xs text-gray-400 mb-0.5">Médecin référent</p>
              <p class="text-sm font-bold text-gray-900">{{ h.medecin }}</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <p class="text-xs text-gray-400 mb-0.5">Service</p>
              <p class="text-sm font-bold text-gray-900">{{ h.service }}</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <p class="text-xs text-gray-400 mb-0.5">Chambre / Lit</p>
              <p class="text-sm font-bold text-violet-700">{{ h.chambre }} · {{ h.lit }}</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <p class="text-xs text-gray-400 mb-0.5">Durée du séjour</p>
              <p class="text-sm font-bold text-gray-900">{{ duree(h.entree, h.sortie_reelle || h.sortie_prev) }} jours</p>
            </div>
          </div>

          <!-- Soins réalisés -->
          <div>
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Soins réalisés</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="s in h.soins" :key="s" class="text-xs bg-blue-50 text-blue-700 border border-blue-100 px-3 py-1 rounded-full font-medium">
                {{ s }}
              </span>
            </div>
          </div>

          <!-- Documents -->
          <div>
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Documents disponibles</p>
            <div class="space-y-2">
              <div v-for="doc in h.documents" :key="doc.nom"
                class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100 hover:border-blue-200 transition-colors">
                <div class="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center text-sm shrink-0">📄</div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-gray-900 truncate">{{ doc.nom }}</p>
                  <p class="text-xs text-gray-400">{{ doc.date }} · {{ doc.type }}</p>
                </div>
                <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition-colors shrink-0">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  Télécharger
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
