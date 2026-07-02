<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = ref('dossier')

const patient = ref({
  id: route.params.id,
  prenom: 'Mamadou', nom: 'Diallo', ddn: '1979-03-15', sexe: 'M',
  telephone: '620 00 00 01', adresse: 'Conakry, Ratoma',
  groupe_sanguin: 'A+', statut: 'Hospitalisé', nss: 'NSS-2025-00001',
  allergies: ['Pénicilline'], antecedents: ['HTA', 'Diabète type 2'],
  medecin_referent: 'Dr. Camara Alpha',
  assurance: 'CNSS Guinée',
})

const tabs = [
  { key: 'dossier',         label: 'Dossier médical', icon: '📋' },
  { key: 'consultations',   label: 'Consultations',   icon: '🩺' },
  { key: 'examens',         label: 'Examens',         icon: '🔬' },
  { key: 'soins',           label: 'Soins',           icon: '💉' },
  { key: 'hospitalisations',label: 'Hospitalisations',icon: '🏥' },
  { key: 'facturation',     label: 'Facturation',     icon: '💳' },
]

const consultations = ref([
  { id: 1, date: '2025-06-10', medecin: 'Dr. Camara', motif: 'Fièvre persistante', diagnostic: 'Paludisme (B54)', traitement: 'Artémether 80mg × 3j', signe: true },
  { id: 2, date: '2025-05-20', medecin: 'Dr. Bah', motif: 'Contrôle HTA', diagnostic: 'HTA essentielle (I10)', traitement: 'Amlodipine 5mg/j', signe: true },
  { id: 3, date: '2025-04-05', medecin: 'Dr. Camara', motif: 'Diabète — bilan', diagnostic: 'Diabète type 2 (E11)', traitement: 'Metformine 500mg × 2/j', signe: true },
])

const examens = ref([
  { id: 1, date: '2025-06-10', type: 'NFS', statut: 'Validé', resultat: 'Hb: 11.2 g/dL · GB: 8500 · Plq: 210000', biologiste: 'Dr. Diallo' },
  { id: 2, date: '2025-06-10', type: 'Glycémie', statut: 'Validé', resultat: '1.42 g/L', biologiste: 'Dr. Diallo' },
  { id: 3, date: '2025-05-20', type: 'ECG', statut: 'Validé', resultat: 'Rythme sinusal normal', biologiste: 'Dr. Sylla' },
])

const soins = ref([
  { id: 1, date: '2025-06-12', heure: '08:00', type: 'Médicament', description: 'Artémether 80mg — voie orale', statut: 'Effectué', infirmier: 'Inf. Kouyaté' },
  { id: 2, date: '2025-06-12', heure: '12:00', type: 'Pansement', description: 'Changement pansement', statut: 'Planifié', infirmier: 'Inf. Kouyaté' },
  { id: 3, date: '2025-06-11', heure: '08:00', type: 'Médicament', description: 'Artémether 80mg — voie orale', statut: 'Effectué', infirmier: 'Inf. Traoré' },
])

const hospitalisations = ref([
  { id: 1, service: 'Médecine interne', chambre: 'C-12', lit: 'L-02', medecin: 'Dr. Camara', entree: '2025-06-08', sortie_prev: '2025-06-15', statut: 'Actif', motif: 'Paludisme sévère' },
])

const factures = ref([
  { id: 'F-2025-001', date: '2025-06-12', type: 'Consultation', montant: 150000, paye: 150000, statut: 'Payée' },
  { id: 'F-2025-002', date: '2025-06-08', type: 'Hospitalisation', montant: 2800000, paye: 1400000, statut: 'Partielle' },
])

const age = computed(() => new Date().getFullYear() - new Date(patient.value.ddn).getFullYear())
function fmt(n) { return n.toLocaleString('fr-FR') + ' GNF' }

const soinStatutColor = { 'Effectué': 'badge-success', 'Planifié': 'badge-info', 'Omis': 'badge-danger' }
const factStatutColor = { 'Payée': 'badge-success', 'Partielle': 'badge-warning', 'En attente': 'badge-danger' }
</script>

<template>
  <div class="space-y-5">

    <!-- Back -->
    <RouterLink to="/patients" class="inline-flex items-center gap-1.5 text-violet-600 hover:text-violet-800 text-sm font-semibold transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Retour à la liste
    </RouterLink>

    <!-- Patient card -->
    <div class="stat-card p-6">
      <div class="flex flex-col sm:flex-row gap-5">
        <div :class="['w-20 h-20 rounded-2xl flex items-center justify-center font-bold text-2xl shrink-0',
          patient.statut === 'Hospitalisé' ? 'bg-blue-100 text-blue-700' : 'bg-violet-100 text-violet-700']">
          {{ patient.prenom[0] }}{{ patient.nom[0] }}
        </div>
        <div class="flex-1">
          <div class="flex flex-wrap items-start justify-between gap-3 mb-3">
            <div>
              <h2 class="text-2xl font-extrabold text-gray-900">{{ patient.prenom }} {{ patient.nom }}</h2>
              <p class="text-gray-500 text-sm">{{ patient.nss }} · {{ patient.sexe === 'M' ? 'Masculin' : 'Féminin' }} · {{ age }} ans</p>
            </div>
            <div class="flex items-center gap-2">
              <span :class="['text-xs font-bold px-3 py-1.5 rounded-full', patient.statut === 'Hospitalisé' ? 'badge-info' : 'badge-success']">
                {{ patient.statut }}
              </span>
              <button class="btn-secondary text-xs py-1.5">Modifier</button>
              <button class="btn-primary text-xs py-1.5">📄 Dossier PDF</button>
            </div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div><p class="text-xs text-gray-400 mb-0.5">Date de naissance</p><p class="text-sm font-semibold">{{ patient.ddn }}</p></div>
            <div><p class="text-xs text-gray-400 mb-0.5">Téléphone</p><p class="text-sm font-semibold">{{ patient.telephone }}</p></div>
            <div>
              <p class="text-xs text-gray-400 mb-0.5">Groupe sanguin</p>
              <p class="text-sm font-extrabold text-red-600">{{ patient.groupe_sanguin }}</p>
            </div>
            <div><p class="text-xs text-gray-400 mb-0.5">Médecin référent</p><p class="text-sm font-semibold">{{ patient.medecin_referent }}</p></div>
            <div><p class="text-xs text-gray-400 mb-0.5">Adresse</p><p class="text-sm font-semibold">{{ patient.adresse }}</p></div>
            <div><p class="text-xs text-gray-400 mb-0.5">Assurance</p><p class="text-sm font-semibold">{{ patient.assurance }}</p></div>
          </div>
          <div class="flex flex-wrap gap-2 mt-4">
            <span v-for="a in patient.allergies" :key="a" class="badge-danger text-xs px-2.5 py-1 rounded-full font-bold">⚠ Allergie : {{ a }}</span>
            <span v-for="ant in patient.antecedents" :key="ant" class="badge-warning text-xs px-2.5 py-1 rounded-full font-semibold">{{ ant }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-white border border-violet-100 rounded-2xl p-1 w-fit overflow-x-auto">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        :class="['flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition-all whitespace-nowrap',
          activeTab === tab.key ? 'bg-violet-600 text-white shadow-sm' : 'text-gray-500 hover:text-violet-600 hover:bg-violet-50']"
      >
        <span>{{ tab.icon }}</span> {{ tab.label }}
      </button>
    </div>

    <!-- Tab content -->
    <div class="stat-card p-5">

      <!-- Dossier -->
      <div v-if="activeTab === 'dossier'" class="space-y-4">
        <p class="section-title">Informations médicales</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="bg-red-50 border border-red-200 rounded-xl p-4">
            <p class="text-xs font-bold text-red-700 mb-2 uppercase tracking-wide">⚠ Allergies connues</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="a in patient.allergies" :key="a" class="badge-danger text-xs px-2.5 py-1 rounded-full font-semibold">{{ a }}</span>
            </div>
          </div>
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <p class="text-xs font-bold text-amber-700 mb-2 uppercase tracking-wide">Antécédents médicaux</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="ant in patient.antecedents" :key="ant" class="badge-warning text-xs px-2.5 py-1 rounded-full font-semibold">{{ ant }}</span>
            </div>
          </div>
        </div>
        <div class="bg-violet-50 border border-violet-200 rounded-xl p-4">
          <p class="text-xs font-bold text-violet-700 mb-2 uppercase tracking-wide">Informations administratives</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
            <div><span class="text-gray-500">NSS :</span> <span class="font-semibold">{{ patient.nss }}</span></div>
            <div><span class="text-gray-500">Assurance :</span> <span class="font-semibold">{{ patient.assurance }}</span></div>
            <div><span class="text-gray-500">Médecin :</span> <span class="font-semibold">{{ patient.medecin_referent }}</span></div>
          </div>
        </div>
      </div>

      <!-- Consultations -->
      <div v-if="activeTab === 'consultations'">
        <div class="flex items-center justify-between mb-4">
          <p class="section-title">Historique des consultations</p>
          <button class="btn-primary text-xs py-1.5">+ Nouvelle consultation</button>
        </div>
        <div class="space-y-3">
          <div v-for="c in consultations" :key="c.id" class="border border-violet-100 rounded-xl p-4 hover:border-violet-300 transition-colors">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-gray-900">{{ c.date }}</span>
                <span class="badge-violet text-xs px-2 py-0.5 rounded-full font-medium">{{ c.medecin }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span v-if="c.signe" class="badge-success text-xs px-2 py-0.5 rounded-full font-medium">✓ Signé</span>
                <button class="text-violet-600 text-xs font-semibold hover:underline">PDF</button>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
              <div><span class="text-gray-400 text-xs">Motif :</span><p class="font-medium text-gray-800">{{ c.motif }}</p></div>
              <div><span class="text-gray-400 text-xs">Diagnostic :</span><p class="font-semibold text-violet-700">{{ c.diagnostic }}</p></div>
              <div><span class="text-gray-400 text-xs">Traitement :</span><p class="font-medium text-gray-800">{{ c.traitement }}</p></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Examens -->
      <div v-if="activeTab === 'examens'">
        <div class="flex items-center justify-between mb-4">
          <p class="section-title">Résultats d'examens</p>
          <button class="btn-primary text-xs py-1.5">+ Prescrire examen</button>
        </div>
        <div class="space-y-3">
          <div v-for="e in examens" :key="e.id" class="border border-gray-100 rounded-xl p-4 hover:border-violet-200 transition-colors">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-gray-900">{{ e.date }}</span>
                <span class="badge-info text-xs px-2 py-0.5 rounded-full font-semibold">{{ e.type }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="badge-success text-xs px-2 py-0.5 rounded-full font-medium">{{ e.statut }}</span>
                <button class="text-violet-600 text-xs font-semibold hover:underline">PDF</button>
              </div>
            </div>
            <p class="text-sm text-gray-700 font-medium">{{ e.resultat }}</p>
            <p class="text-xs text-gray-400 mt-1">Validé par {{ e.biologiste }}</p>
          </div>
        </div>
      </div>

      <!-- Soins -->
      <div v-if="activeTab === 'soins'">
        <div class="flex items-center justify-between mb-4">
          <p class="section-title">Plan de soins</p>
          <button class="btn-primary text-xs py-1.5">+ Ajouter soin</button>
        </div>
        <div class="space-y-2">
          <div v-for="s in soins" :key="s.id"
            :class="['flex items-center gap-4 p-3 rounded-xl border', s.statut === 'Omis' ? 'border-red-200 bg-red-50' : 'border-gray-100 bg-gray-50']">
            <div class="text-center shrink-0">
              <p class="text-xs font-bold text-violet-700 font-mono">{{ s.heure }}</p>
              <p class="text-[10px] text-gray-400">{{ s.date }}</p>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900">{{ s.description }}</p>
              <p class="text-xs text-gray-500">{{ s.type }} · {{ s.infirmier }}</p>
            </div>
            <span :class="['text-xs font-bold px-2.5 py-1 rounded-full shrink-0', soinStatutColor[s.statut] || 'badge-info']">
              {{ s.statut }}
            </span>
          </div>
        </div>
      </div>

      <!-- Hospitalisations -->
      <div v-if="activeTab === 'hospitalisations'">
        <div class="flex items-center justify-between mb-4">
          <p class="section-title">Séjours hospitaliers</p>
          <button class="btn-primary text-xs py-1.5">+ Nouvelle admission</button>
        </div>
        <div v-for="h in hospitalisations" :key="h.id" class="border border-violet-100 rounded-xl p-4">
          <div class="flex items-center justify-between mb-3">
            <span :class="['text-xs font-bold px-3 py-1 rounded-full', h.statut === 'Actif' ? 'badge-success' : 'badge-violet']">
              {{ h.statut }}
            </span>
            <span class="badge-violet text-xs px-2 py-0.5 rounded-full font-medium">{{ h.service }}</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            <div><p class="text-xs text-gray-400">Chambre / Lit</p><p class="font-bold text-violet-700">{{ h.chambre }} · {{ h.lit }}</p></div>
            <div><p class="text-xs text-gray-400">Médecin</p><p class="font-semibold">{{ h.medecin }}</p></div>
            <div><p class="text-xs text-gray-400">Entrée</p><p class="font-semibold">{{ h.entree }}</p></div>
            <div><p class="text-xs text-gray-400">Sortie prévue</p><p class="font-semibold">{{ h.sortie_prev }}</p></div>
          </div>
          <p class="text-sm text-gray-600 mt-2"><span class="font-medium">Motif :</span> {{ h.motif }}</p>
        </div>
      </div>

      <!-- Facturation -->
      <div v-if="activeTab === 'facturation'">
        <div class="flex items-center justify-between mb-4">
          <p class="section-title">Factures</p>
          <button class="btn-primary text-xs py-1.5">+ Nouvelle facture</button>
        </div>
        <div class="space-y-3">
          <div v-for="f in factures" :key="f.id" class="flex items-center gap-4 p-4 border border-gray-100 rounded-xl hover:border-violet-200 transition-colors">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-mono text-xs font-bold text-violet-700">{{ f.id }}</span>
                <span class="badge-info text-xs px-2 py-0.5 rounded-full font-medium">{{ f.type }}</span>
              </div>
              <p class="text-xs text-gray-400">{{ f.date }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-bold text-gray-900">{{ fmt(f.montant) }}</p>
              <p class="text-xs text-green-600 font-semibold">Payé : {{ fmt(f.paye) }}</p>
            </div>
            <span :class="['text-xs font-bold px-2.5 py-1 rounded-full', factStatutColor[f.statut]]">{{ f.statut }}</span>
            <button class="text-violet-600 text-xs font-semibold hover:underline">PDF</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
