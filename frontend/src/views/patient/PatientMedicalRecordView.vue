<script setup>
import { ref, computed } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import ChartComponent from '@/components/ChartComponent.vue'

const i18n = useI18nStore()
const activeTab = ref('overview')

const patient = ref({
  prenom: 'Mamadou', nom: 'Diallo', ddn: '1979-03-15',
  groupe_sanguin: 'A+', nss: 'PAT-00001', medecin: 'Dr. Camara Alpha',
  allergies: ['Pénicilline'], assurance: 'CNSS Guinée',
})

const tabs = [
  { key: 'overview', label: 'Vue d\'ensemble', icon: '📊' },
  { key: 'history', label: 'Historique', icon: '📋' },
  { key: 'results', label: 'Résultats', icon: '🔬' },
  { key: 'prescriptions', label: 'Ordonnances', icon: '💊' },
  { key: 'hospitalizations', label: 'Hospitalisations', icon: '🏥' },
  { key: 'imaging', label: 'Imagerie', icon: '🩻' },
  { key: 'vitals', label: 'Signes vitaux', icon: '❤️' },
]

const vitalsHistory = ref([
  { date: '2025-06-01', tension: '130/85', pouls: 78, temperature: 36.8, o2: 98, poids: 75 },
  { date: '2025-05-15', tension: '135/88', pouls: 82, temperature: 36.9, o2: 97, poids: 76 },
  { date: '2025-04-20', tension: '128/82', pouls: 75, temperature: 36.7, o2: 99, poids: 77 },
  { date: '2025-03-10', tension: '140/90', pouls: 85, temperature: 37.0, o2: 96, poids: 78 },
  { date: '2025-02-15', tension: '142/92', pouls: 88, temperature: 36.6, o2: 97, poids: 80 },
])

const consultationHistory = ref([
  { date: '2025-06-10', medecin: 'Dr. Camara Alpha', service: 'Médecine Interne', motif: 'Consultation de suivi', diagnostic: 'HTA stable', prescription: 'Continuer Amlodipine 5mg' },
  { date: '2025-05-20', medecin: 'Dr. Diallo Oumar', service: 'Cardiologie', motif: 'ECG de contrôle', diagnostic: 'Rythme sinusal normal', prescription: 'Pas de changement' },
  { date: '2025-04-15', medecin: 'Dr. Camara Alpha', service: 'Médecine Interne', motif: 'Contrôle diabète', diagnostic: 'Diabète type 2 contrôlé', prescription: 'Metformine 500mg 2x/j' },
  { date: '2025-03-05', medecin: 'Dr. Bah Mariama', service: 'Cardiologie', motif: 'Douleurs thoraciques', diagnostic: 'Angine de poitrine', prescription: 'Nitroglycérine SL + ECG' },
])

const hospitalizations = ref([
  { dateDebut: '2025-01-10', dateFin: '2025-01-18', service: 'Chirurgie générale', motif: 'Appendicite', medecin: 'Dr. Barry Mamadou', statut: 'Terminée' },
  { dateDebut: '2024-08-15', dateFin: '2024-08-22', service: 'Médecine interne', motif: 'Crise diabétique', medecin: 'Dr. Camara Alpha', statut: 'Terminée' },
])

const medications = ref([
  { nom: 'Amlodipine', posologie: '5mg, 1 comprimé le matin', frequency: 'Quotidien', duration: 'Traitement long', status: 'Actif' },
  { nom: 'Metformine', posologie: '500mg, 1 comprimé matin et soir', frequency: '2x/jour', duration: 'Traitement long', status: 'Actif' },
  { nom: 'Nitroglycérine', posologie: '0.4mg SL en cas de douleur', frequency: 'Selon besoin', duration: 'Au besoin', status: 'Actif' },
])

const chartData = {
  labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
  data: [142, 140, 135, 128, 135, 130],
  title: 'Évolution de la tension systolique (mmHg)',
}

const vitalTrends = {
  labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
  data: [80, 78, 77, 76, 76, 75],
  title: 'Évolution du poids (kg)',
}
</script>

<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Mon Dossier Médical</h1>
        <p class="text-sm text-gray-500 mt-1">Consultez et gérez votre historique médical complet</p>
      </div>
      <div class="flex gap-2">
        <button type="button" class="btn-secondary" @click="alert('📄 Téléchargement du dossier en PDF...')">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Télécharger PDF
        </button>
        <button type="button" class="btn-primary" @click="alert('📤 Export du dossier médical...')">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
          </svg>
          Exporter
        </button>
      </div>
    </div>

    <!-- Carte patient -->
    <div class="bg-gradient-to-r from-blue-600 to-cyan-500 rounded-2xl p-6 text-white">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center text-2xl font-extrabold shrink-0">
            {{ patient.prenom[0] }}{{ patient.nom[0] }}
          </div>
          <div>
            <p class="text-blue-100 text-sm">Dossier médical de</p>
            <h2 class="text-2xl font-extrabold">{{ patient.prenom }} {{ patient.nom }}</h2>
            <p class="text-blue-200 text-sm mt-0.5">{{ patient.nss }} · NSS · Né(e) le {{ patient.ddn }}</p>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <div class="bg-white/15 border border-white/20 rounded-xl px-4 py-2 text-center">
            <p class="text-xs text-blue-200">Groupe sanguin</p>
            <p class="text-xl font-extrabold">{{ patient.groupe_sanguin }}</p>
          </div>
          <div class="bg-white/15 border border-white/20 rounded-xl px-4 py-2 text-center">
            <p class="text-xs text-blue-200">Médecin traitant</p>
            <p class="text-sm font-bold">{{ patient.medecin }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Onglets -->
    <div class="bg-white rounded-2xl border border-gray-100 p-2 flex gap-1 overflow-x-auto">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        :class="['flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all whitespace-nowrap',
          activeTab === tab.key ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700']">
        <span>{{ tab.icon }}</span>
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- Contenu des onglets -->
    <div class="space-y-6">
      <!-- Vue d'ensemble -->
      <div v-if="activeTab === 'overview'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartComponent :data="chartData.data" :labels="chartData.labels" :title="chartData.title" />
        <ChartComponent :data="vitalTrends.data" :labels="vitalTrends.labels" :title="vitalTrends.title" />
        
        <!-- Médications actives -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5 lg:col-span-2">
          <h3 class="font-bold text-gray-900 mb-4">💊 Médications actives</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div v-for="med in medications" :key="med.nom"
              class="p-4 bg-blue-50 rounded-xl border border-blue-100">
              <p class="font-bold text-gray-900">{{ med.nom }}</p>
              <p class="text-xs text-gray-600 mt-1">{{ med.posologie }}</p>
              <p class="text-xs text-blue-600 font-semibold mt-2">{{ med.frequency }}</p>
            </div>
          </div>
        </div>

        <!-- Prochains rendez-vous -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 class="font-bold text-gray-900 mb-4">📅 Prochains rendez-vous</h3>
          <div class="space-y-3">
            <div v-for="rdv in [
              { date: '2025-06-18', time: '09:30', medecin: 'Dr. Camara Alpha', service: 'Médecine Interne', type: 'Suivi HTA' },
              { date: '2025-07-03', time: '14:30', medecin: 'Dr. Bah Mariama', service: 'Cardiologie', type: 'ECG de contrôle' },
            ]" :key="rdv.date" class="flex items-center gap-4 p-3 rounded-xl bg-gray-50">
              <div class="w-12 h-12 rounded-xl bg-blue-100 flex flex-col items-center justify-center shrink-0">
                <p class="text-sm font-extrabold text-blue-700 leading-none">{{ new Date(rdv.date).getDate() }}</p>
                <p class="text-[10px] text-blue-500 uppercase font-semibold">{{ new Date(rdv.date).toLocaleDateString('fr-FR', { month: 'short' }) }}</p>
              </div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900 text-sm">{{ rdv.type }}</p>
                <p class="text-xs text-gray-500">{{ rdv.medecin }} · {{ rdv.service }}</p>
              </div>
              <span class="text-xs font-bold text-blue-600">{{ rdv.time }}</span>
            </div>
          </div>
        </div>

        <!-- Résumé santé -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 class="font-bold text-gray-900 mb-4">📊 Résumé de santé</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <span class="text-sm text-gray-600">IMC</span>
              <span class="font-bold text-gray-900">24.5 (Normal)</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <span class="text-sm text-gray-600">Tension artérielle</span>
              <span class="font-bold text-gray-900">130/85 mmHg</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <span class="text-sm text-gray-600">Glycémie à jeun</span>
              <span class="font-bold text-gray-900">1.05 g/L</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <span class="text-sm text-gray-600">Cholestérol total</span>
              <span class="font-bold text-gray-900">1.80 g/L</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Historique consultations -->
      <div v-if="activeTab === 'history'" class="bg-white rounded-2xl border border-gray-100 p-5">
        <h3 class="font-bold text-gray-900 mb-4">📋 Historique des consultations</h3>
        <div class="space-y-4">
          <div v-for="(c, i) in consultationHistory" :key="i"
            class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:border-blue-200 transition-colors">
            <div class="flex items-start justify-between gap-4 flex-wrap mb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm">
                  {{ new Date(c.date).getDate() }}
                </div>
                <div>
                  <p class="font-bold text-gray-900">{{ c.medecin }}</p>
                  <p class="text-xs text-gray-500">{{ c.service }} · {{ c.date }}</p>
                </div>
              </div>
              <span class="text-xs font-bold bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full">{{ c.motif }}</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-xs text-gray-500">Diagnostic :</span>
                <p class="font-semibold text-gray-900">{{ c.diagnostic }}</p>
              </div>
              <div>
                <span class="text-xs text-gray-500">Prescription :</span>
                <p class="font-semibold text-gray-900">{{ c.prescription }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Signes vitaux -->
      <div v-if="activeTab === 'vitals'" class="space-y-6">
        <ChartComponent :data="[130, 135, 128, 140, 142, 130]" :labels="['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']" title="Tension artérielle systolique (mmHg)" />
        
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 class="font-bold text-gray-900 mb-4">📈 Historique des signes vitaux</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="table-header">
                  <th class="px-4 py-3 text-left font-bold text-gray-700">Date</th>
                  <th class="px-4 py-3 text-left font-bold text-gray-700">Tension</th>
                  <th class="px-4 py-3 text-left font-bold text-gray-700">Pouls</th>
                  <th class="px-4 py-3 text-left font-bold text-gray-700">Température</th>
                  <th class="px-4 py-3 text-left font-bold text-gray-700">O2</th>
                  <th class="px-4 py-3 text-left font-bold text-gray-700">Poids</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(v, i) in vitalsHistory" :key="i" class="table-row">
                  <td class="px-4 py-3 font-semibold text-gray-900">{{ v.date }}</td>
                  <td class="px-4 py-3" :class="v.tension.split('/')[0] > 140 ? 'text-red-600 font-bold' : 'text-gray-700'">{{ v.tension }}</td>
                  <td class="px-4 py-3 text-gray-700">{{ v.pouls }} bpm</td>
                  <td class="px-4 py-3 text-gray-700">{{ v.temperature }}°C</td>
                  <td class="px-4 py-3" :class="v.o2 < 95 ? 'text-red-600 font-bold' : 'text-gray-700'">{{ v.o2 }}%</td>
                  <td class="px-4 py-3 text-gray-700">{{ v.poids }} kg</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Autres onglets (simplifiés) -->
      <div v-if="['results', 'prescriptions', 'hospitalizations', 'imaging'].includes(activeTab)"
        class="bg-white rounded-2xl border border-gray-100 p-8 text-center">
        <span class="text-5xl block mb-4">{{ activeTab === 'results' ? '🔬' : activeTab === 'prescriptions' ? '💊' : activeTab === 'hospitalizations' ? '🏥' : '🩻' }}</span>
        <h3 class="text-lg font-bold text-gray-900 mb-2">
          {{ activeTab === 'results' ? 'Résultats d\'examens' : activeTab === 'prescriptions' ? 'Ordonnances' : activeTab === 'hospitalizations' ? 'Historique des hospitalisations' : 'Examens d\'imagerie' }}
        </h3>
        <p class="text-sm text-gray-500 mb-4">Cette section contient tous vos {{ activeTab === 'results' ? 'résultats de laboratoire et examens' : activeTab === 'prescriptions' ? 'ordonnances passées et actuelles' : activeTab === 'hospitalizations' ? 'hospitalisations passées' : 'examens d\'imagerie (radio, scanner, IRM, échographie)' }}.</p>
        <button type="button" class="btn-primary" @click="alert('👁️ Affichage de tous les résultats...')">Voir tout</button>
      </div>
    </div>
  </div>
</template>
