<script setup>
import { ref, computed } from 'vue'

const patient = ref({
  prenom: 'Mamadou', nom: 'Diallo', ddn: '1979-03-15',
  groupe_sanguin: 'A+', medecin: 'Dr. Camara Alpha',
  nss: 'PAT-00001', assurance: 'CNSS Guinée',
  allergies: ['Pénicilline'],
})

const prochainsRdv = ref([
  { id: 1, date: '2025-06-18', heure: '09:30', medecin: 'Dr. Camara Alpha', service: 'Médecine interne', lieu: 'Bâtiment A — Salle 12', type: 'Consultation de suivi',  statut: 'Confirmé' },
  { id: 2, date: '2025-06-25', heure: '11:00', medecin: 'Dr. Diallo Oumar',  service: 'Laboratoire',      lieu: 'Centre de prélèvement', type: 'Bilan sanguin',          statut: 'Confirmé' },
  { id: 3, date: '2025-07-03', heure: '14:30', medecin: 'Dr. Bah Mariama',   service: 'Cardiologie',      lieu: 'Bâtiment C — Salle 5',  type: 'ECG de contrôle',       statut: 'En attente' },
])

const derniersResultats = ref([
  { id: 1, date: '2025-06-10', type: 'NFS',      nouveau: true },
  { id: 2, date: '2025-06-10', type: 'Glycémie', nouveau: true },
  { id: 3, date: '2025-05-20', type: 'ECG',      nouveau: false },
])

const messages = ref([
  { id: 1, de: 'Dr. Camara Alpha',    sujet: 'Résultats de votre bilan',      date: '2025-06-11', lu: false },
  { id: 2, de: 'Secrétariat médical', sujet: 'Confirmation RDV du 18 juin',   date: '2025-06-10', lu: true },
])

const prochainRdv = computed(() => prochainsRdv.value[0])
const joursAvant = computed(() => {
  const diff = new Date(prochainRdv.value.date) - new Date()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})

const accesRapides = [
  { icon: '📅', label: 'Prendre RDV',      path: '/patient/rendez-vous',     color: 'bg-blue-600' },
  { icon: '🔬', label: 'Mes résultats',    path: '/patient/resultats',        color: 'bg-teal-600' },
  { icon: '🫁', label: 'Imagerie',          path: '/patient/imagerie',         color: 'bg-cyan-600' },
  { icon: '💊', label: 'Mes ordonnances',  path: '/patient/ordonnances',      color: 'bg-violet-600' },
  { icon: '💳', label: 'Mes factures',     path: '/patient/factures',         color: 'bg-green-600' },
  { icon: '💬', label: 'Messagerie',       path: '/patient/messagerie',       color: 'bg-orange-500' },
  { icon: '📝', label: 'Admission',        path: '/patient/admission',        color: 'bg-indigo-600' },
  { icon: '🔗', label: 'Partage dossier',  path: '/patient/partage',          color: 'bg-purple-600' },
  { icon: '📖', label: 'Livret d\'accueil',path: '/patient/livret',           color: 'bg-slate-600' },
  { icon: '🏥', label: 'Hospitalisations', path: '/patient/hospitalisations', color: 'bg-red-600' },
]
</script>

<template>
  <div class="space-y-6">

    <!-- Carte patient -->
    <div class="bg-gradient-to-r from-blue-600 to-cyan-500 rounded-2xl p-6 text-white">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center text-2xl font-extrabold shrink-0">
            {{ patient.prenom[0] }}{{ patient.nom[0] }}
          </div>
          <div>
            <p class="text-blue-100 text-sm">Bonjour,</p>
            <h1 class="text-2xl font-extrabold">{{ patient.prenom }} {{ patient.nom }}</h1>
            <p class="text-blue-200 text-sm mt-0.5">{{ patient.nss }} · {{ patient.medecin }}</p>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <div class="bg-white/15 border border-white/20 rounded-xl px-4 py-2 text-center">
            <p class="text-xs text-blue-200">Groupe sanguin</p>
            <p class="text-xl font-extrabold">{{ patient.groupe_sanguin }}</p>
          </div>
          <div class="bg-white/15 border border-white/20 rounded-xl px-4 py-2 text-center">
            <p class="text-xs text-blue-200">Assurance</p>
            <p class="text-sm font-bold">{{ patient.assurance }}</p>
          </div>
          <div v-if="patient.allergies.length" class="bg-red-500/30 border border-red-300/30 rounded-xl px-4 py-2 text-center">
            <p class="text-xs text-red-200">⚠ Allergie</p>
            <p class="text-sm font-bold">{{ patient.allergies[0] }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Prochain RDV en évidence -->
    <div v-if="prochainRdv" class="bg-white rounded-2xl border-2 border-blue-200 p-5 shadow-sm">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div class="flex items-start gap-4">
          <div class="w-16 h-16 rounded-2xl bg-blue-600 flex flex-col items-center justify-center text-white shrink-0">
            <p class="text-xl font-extrabold leading-none">{{ new Date(prochainRdv.date).getDate() }}</p>
            <p class="text-xs font-semibold uppercase">{{ new Date(prochainRdv.date).toLocaleDateString('fr-FR', { month: 'short' }) }}</p>
          </div>
          <div>
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span class="text-xs font-bold bg-blue-100 text-blue-700 px-2.5 py-0.5 rounded-full">Prochain rendez-vous</span>
              <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', prochainRdv.statut === 'Confirmé' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700']">
                {{ prochainRdv.statut }}
              </span>
            </div>
            <h3 class="font-extrabold text-gray-900 text-lg">{{ prochainRdv.type }}</h3>
            <p class="text-gray-600 text-sm">{{ prochainRdv.medecin }} · {{ prochainRdv.service }}</p>
            <p class="text-gray-500 text-sm mt-1">📍 {{ prochainRdv.lieu }} &nbsp;·&nbsp; 🕐 {{ prochainRdv.heure }}</p>
          </div>
        </div>
        <div class="text-right shrink-0">
          <div :class="['text-3xl font-extrabold', joursAvant <= 3 ? 'text-red-600' : joursAvant <= 7 ? 'text-amber-600' : 'text-blue-600']">
            J-{{ joursAvant }}
          </div>
          <p class="text-xs text-gray-400 mb-3">jours restants</p>
          <div class="flex gap-2">
            <button class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors">📲 Rappel</button>
            <button class="text-xs font-semibold px-3 py-1.5 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors">Annuler</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Accès rapides -->
    <div>
      <h2 class="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">Accès rapides</h2>
      <div class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-10 gap-3">
        <RouterLink v-for="a in accesRapides" :key="a.path" :to="a.path"
          class="flex flex-col items-center gap-2 p-4 bg-white rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all group">
          <div :class="['w-11 h-11 rounded-xl flex items-center justify-center text-white text-xl', a.color]">{{ a.icon }}</div>
          <span class="text-xs font-semibold text-gray-700 text-center leading-tight group-hover:text-blue-700">{{ a.label }}</span>
        </RouterLink>
      </div>
    </div>

    <!-- Grille bas -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

      <!-- Liste RDV -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5 md:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-gray-900">Mes prochains rendez-vous</h2>
          <RouterLink to="/patient/rendez-vous" class="text-xs text-blue-600 font-semibold hover:underline">Voir tout →</RouterLink>
        </div>
        <div class="space-y-3">
          <div v-for="rdv in prochainsRdv" :key="rdv.id"
            class="flex items-center gap-4 p-3 rounded-xl bg-gray-50 hover:bg-blue-50/50 transition-colors">
            <div class="w-12 h-12 rounded-xl bg-blue-100 flex flex-col items-center justify-center shrink-0">
              <p class="text-sm font-extrabold text-blue-700 leading-none">{{ new Date(rdv.date).getDate() }}</p>
              <p class="text-[10px] text-blue-500 uppercase font-semibold">{{ new Date(rdv.date).toLocaleDateString('fr-FR', { month: 'short' }) }}</p>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm truncate">{{ rdv.type }}</p>
              <p class="text-xs text-gray-500 truncate">{{ rdv.medecin }} · {{ rdv.heure }}</p>
            </div>
            <span :class="['text-xs font-bold px-2.5 py-1 rounded-full shrink-0',
              rdv.statut === 'Confirmé' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700']">
              {{ rdv.statut }}
            </span>
          </div>
        </div>
        <RouterLink to="/patient/rendez-vous"
          class="mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border-2 border-dashed border-blue-200 text-blue-600 text-sm font-semibold hover:bg-blue-50 transition-colors">
          + Prendre un nouveau rendez-vous
        </RouterLink>
      </div>

      <!-- Colonne droite -->
      <div class="space-y-4">
        <!-- Nouveaux résultats -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-bold text-gray-900 text-sm">Nouveaux résultats</h2>
            <RouterLink to="/patient/resultats" class="text-xs text-teal-600 font-semibold hover:underline">Voir →</RouterLink>
          </div>
          <div class="space-y-2">
            <div v-for="r in derniersResultats.filter(r => r.nouveau)" :key="r.id"
              class="flex items-center gap-3 p-2.5 rounded-xl bg-teal-50 border border-teal-100">
              <div class="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center text-white text-sm shrink-0">🔬</div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-gray-900">{{ r.type }}</p>
                <p class="text-[10px] text-gray-500">{{ r.date }}</p>
              </div>
              <span class="w-2 h-2 rounded-full bg-teal-500 shrink-0"></span>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div class="bg-white rounded-2xl border border-gray-100 p-5">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-bold text-gray-900 text-sm">Messages</h2>
            <RouterLink to="/patient/messagerie" class="text-xs text-orange-600 font-semibold hover:underline">Voir →</RouterLink>
          </div>
          <div class="space-y-2">
            <div v-for="m in messages" :key="m.id"
              :class="['flex items-start gap-3 p-2.5 rounded-xl', !m.lu ? 'bg-orange-50 border border-orange-100' : 'bg-gray-50']">
              <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-sm shrink-0">💬</div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-gray-900 truncate">{{ m.de }}</p>
                <p class="text-[10px] text-gray-500 truncate">{{ m.sujet }}</p>
              </div>
              <div v-if="!m.lu" class="w-2 h-2 rounded-full bg-orange-500 mt-1 shrink-0"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
