<script setup>
import { ref } from 'vue'

const activeExamen = ref(null)

const examens = ref([
  {
    id: 1, date: '2025-06-10', type: 'Radiographie thoracique', modalite: 'RX',
    prescripteur: 'Dr. Camara Alpha', radiologue: 'Dr. Sylla Kadiatou',
    statut: 'Disponible', nouveau: true,
    compte_rendu: 'Pas d\'anomalie parenchymateuse visible. Silhouette cardiaque de taille normale. Coupoles diaphragmatiques en place. Pas d\'épanchement pleural.',
    conclusion: 'Radiographie thoracique normale.',
    images: [
      { id: 1, label: 'Face', thumb: '🫁', description: 'Incidence de face' },
      { id: 2, label: 'Profil', thumb: '🫁', description: 'Incidence de profil' },
    ]
  },
  {
    id: 2, date: '2025-05-20', type: 'Échographie abdominale', modalite: 'ECHO',
    prescripteur: 'Dr. Bah Mariama', radiologue: 'Dr. Diallo Oumar',
    statut: 'Disponible', nouveau: false,
    compte_rendu: 'Foie de taille normale, contours réguliers, échostructure homogène. Vésicule biliaire sans lithiase visible. Reins de taille et d\'échostructure normaux. Pas d\'épanchement péritonéal.',
    conclusion: 'Échographie abdominale sans anomalie significative.',
    images: [
      { id: 1, label: 'Foie', thumb: '🫀', description: 'Coupe longitudinale foie' },
      { id: 2, label: 'Rein droit', thumb: '🫀', description: 'Coupe longitudinale rein droit' },
      { id: 3, label: 'Rein gauche', thumb: '🫀', description: 'Coupe longitudinale rein gauche' },
    ]
  },
  {
    id: 3, date: '2025-04-05', type: 'ECG 12 dérivations', modalite: 'ECG',
    prescripteur: 'Dr. Bah Mariama', radiologue: 'Dr. Bah Mariama',
    statut: 'Disponible', nouveau: false,
    compte_rendu: 'Rythme sinusal régulier à 72 bpm. Axe normal. Pas de trouble de la repolarisation. Pas de signe d\'hypertrophie ventriculaire.',
    conclusion: 'ECG normal.',
    images: [{ id: 1, label: 'Tracé ECG', thumb: '📈', description: '12 dérivations' }]
  },
])

const modaliteColor = {
  'RX':   'bg-blue-100 text-blue-700',
  'ECHO': 'bg-teal-100 text-teal-700',
  'ECG':  'bg-violet-100 text-violet-700',
  'IRM':  'bg-orange-100 text-orange-700',
  'TDM':  'bg-red-100 text-red-700',
}
</script>

<template>
  <div class="space-y-5">
    <div>
      <h1 class="text-2xl font-extrabold text-gray-900">Portail d'imagerie médicale</h1>
      <p class="text-sm text-gray-500 mt-0.5">Consultez vos examens d'imagerie et comptes-rendus radiologiques en ligne</p>
    </div>

    <!-- Info accès -->
    <div class="alert-info-banner flex items-start gap-3">
      <span class="text-blue-700 text-lg shrink-0">ℹ️</span>
      <div>
        <p class="text-sm font-bold text-blue-900">Accès sécurisé à vos images médicales</p>
        <p class="text-sm text-blue-800">Vos examens d'imagerie sont disponibles en ligne 24h/24. Les images DICOM peuvent être téléchargées pour être partagées avec un autre médecin.</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">

      <!-- Liste examens -->
      <div class="lg:col-span-2 space-y-3">
        <h2 class="text-sm font-bold text-gray-700 uppercase tracking-wide">Mes examens ({{ examens.length }})</h2>
        <div v-for="e in examens" :key="e.id"
          @click="activeExamen = activeExamen?.id === e.id ? null : e"
          :class="['bg-white rounded-2xl border-2 p-4 cursor-pointer transition-all hover:shadow-md',
            activeExamen?.id === e.id ? 'border-blue-500 shadow-md' : 'border-gray-100 hover:border-blue-200']">
          <div class="flex items-start gap-3">
            <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0', activeExamen?.id === e.id ? 'bg-blue-600 text-white' : 'bg-gray-100']">
              🔬
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <p class="font-bold text-gray-900 text-sm truncate">{{ e.type }}</p>
                <span v-if="e.nouveau" class="text-[10px] font-bold bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">NOUVEAU</span>
              </div>
              <div class="flex items-center gap-2 flex-wrap">
                <span :class="['text-[10px] font-bold px-2 py-0.5 rounded-full', modaliteColor[e.modalite] || 'bg-gray-100 text-gray-600']">{{ e.modalite }}</span>
                <span class="text-xs text-gray-400">{{ e.date }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-1 truncate">{{ e.radiologue }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Visionneuse + compte-rendu -->
      <div class="lg:col-span-3">
        <div v-if="!activeExamen" class="bg-white rounded-2xl border border-gray-100 p-12 text-center text-gray-400">
          <div class="text-5xl mb-3">🔬</div>
          <p class="font-semibold">Sélectionnez un examen</p>
          <p class="text-sm mt-1">pour consulter les images et le compte-rendu</p>
        </div>

        <div v-else class="space-y-4">

          <!-- Header examen -->
          <div class="bg-white rounded-2xl border border-gray-100 p-5">
            <div class="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <div class="flex items-center gap-2 mb-1 flex-wrap">
                  <h2 class="font-extrabold text-gray-900">{{ activeExamen.type }}</h2>
                  <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', modaliteColor[activeExamen.modalite]]">{{ activeExamen.modalite }}</span>
                </div>
                <p class="text-sm text-gray-500">{{ activeExamen.date }} · Prescrit par {{ activeExamen.prescripteur }}</p>
                <p class="text-sm text-gray-500">Interprété par {{ activeExamen.radiologue }}</p>
              </div>
              <div class="flex gap-2">
                <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  PDF
                </button>
                <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-gray-200 text-gray-600 text-xs font-semibold hover:bg-gray-50 transition-colors">
                  📦 DICOM
                </button>
              </div>
            </div>
          </div>

          <!-- Visionneuse images -->
          <div class="bg-white rounded-2xl border border-gray-100 p-5">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Images ({{ activeExamen.images.length }})</p>
            <div class="grid grid-cols-3 gap-3">
              <div v-for="img in activeExamen.images" :key="img.id"
                class="aspect-square bg-gray-900 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all group relative overflow-hidden">
                <span class="text-4xl">{{ img.thumb }}</span>
                <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/>
                  </svg>
                  <span class="text-white text-xs font-semibold">Agrandir</span>
                </div>
                <p class="absolute bottom-1 left-0 right-0 text-center text-[10px] text-gray-300 font-medium">{{ img.label }}</p>
              </div>
            </div>
            <p class="text-xs text-gray-400 mt-3 text-center">
              💡 Cliquez sur une image pour l'agrandir · Téléchargez le fichier DICOM pour une visualisation complète
            </p>
          </div>

          <!-- Compte-rendu -->
          <div class="bg-white rounded-2xl border border-gray-100 p-5">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Compte-rendu radiologique</p>
            <div class="bg-gray-50 rounded-xl p-4 mb-3">
              <p class="text-xs font-bold text-gray-700 mb-2">Description</p>
              <p class="text-sm text-gray-700 leading-relaxed">{{ activeExamen.compte_rendu }}</p>
            </div>
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p class="text-xs font-bold text-blue-700 mb-1">Conclusion</p>
              <p class="text-sm font-semibold text-gray-900">{{ activeExamen.conclusion }}</p>
            </div>
            <div class="mt-3 flex items-center gap-2 text-xs text-gray-400">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
              Compte-rendu validé et signé électroniquement par {{ activeExamen.radiologue }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
