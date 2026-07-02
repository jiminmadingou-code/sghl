<script setup>
import { ref } from 'vue'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const showModal = ref(false)
const form = ref({ specialite: '', medecin: '', date: '', heure: '', motif: '' })

const rdvs = ref([
  { id: 1, date: '2025-06-18', heure: '09:30', medecin: 'Dr. Camara Alpha', service: 'Médecine interne', lieu: 'Bâtiment A — Salle 12', type: 'Consultation de suivi',  statut: 'Confirmé',   instructions: 'Venir à jeun. Apporter vos derniers résultats.' },
  { id: 2, date: '2025-06-25', heure: '11:00', medecin: 'Dr. Diallo Oumar',  service: 'Laboratoire',      lieu: 'Centre de prélèvement', type: 'Bilan sanguin',          statut: 'Confirmé',   instructions: 'Venir à jeun depuis 12h. Apporter la prescription.' },
  { id: 3, date: '2025-07-03', heure: '14:30', medecin: 'Dr. Bah Mariama',   service: 'Cardiologie',      lieu: 'Bâtiment C — Salle 5',  type: 'ECG de contrôle',       statut: 'En attente', instructions: '' },
])

const historique = ref([
  { id: 4, date: '2025-06-10', heure: '10:00', medecin: 'Dr. Camara Alpha', service: 'Médecine interne', type: 'Consultation', statut: 'Effectué' },
  { id: 5, date: '2025-05-20', heure: '09:00', medecin: 'Dr. Bah Mariama',  service: 'Cardiologie',      type: 'Consultation', statut: 'Effectué' },
  { id: 6, date: '2025-04-15', heure: '11:30', medecin: 'Dr. Camara Alpha', service: 'Médecine interne', type: 'Consultation', statut: 'Annulé' },
])

const specialites = ['Médecine interne', 'Cardiologie', 'Pédiatrie', 'Maternité', 'Neurologie', 'Chirurgie générale', 'Ophtalmologie', 'Laboratoire']
const creneaux = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00']

function joursAvant(date) {
  return Math.max(0, Math.ceil((new Date(date) - new Date()) / (1000 * 60 * 60 * 24)))
}

function setRappel(rdv) {
  toast.success(`Rappel activé pour votre RDV du ${rdv.date} à ${rdv.heure} — Vous serez notifié 24h avant`)
}

function annulerRdv(rdv) {
  if (confirm(`Annuler le RDV "${rdv.type}" du ${rdv.date} ?`)) {
    rdv.statut = 'Annulé'
    toast.warning(`RDV du ${rdv.date} annulé. Le secrétariat a été notifié.`)
  }
}

function confirmerRdv() {
  rdvs.value.unshift({
    id: Date.now(), date: form.value.date, heure: form.value.heure,
    medecin: form.value.medecin || 'À confirmer', service: form.value.specialite,
    lieu: 'À confirmer', type: form.value.motif, statut: 'En attente', instructions: ''
  })
  showModal.value = false
  form.value = { specialite: '', medecin: '', date: '', heure: '', motif: '' }
  toast.success('Demande de RDV envoyée ! Confirmation par SMS sous 24h.')
}

const statutColor = { 'Confirmé': 'badge-success', 'En attente': 'badge-warning', 'Effectué': 'badge-info', 'Annulé': 'badge-danger' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Mes rendez-vous</h1>
        <p class="text-sm text-gray-500 mt-0.5">Gérez vos consultations et prenez de nouveaux rendez-vous</p>
      </div>
      <button @click="showModal = true" class="btn-primary">+ Prendre un rendez-vous</button>
    </div>

    <!-- RDV à venir -->
    <div>
      <h2 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Rendez-vous à venir ({{ rdvs.filter(r => r.statut !== 'Annulé').length }})</h2>
      <div class="space-y-3">
        <div v-for="rdv in rdvs" :key="rdv.id"
          :class="['bg-white rounded-2xl border-2 p-5 transition-all', rdv.statut === 'Annulé' ? 'border-gray-200 opacity-60' : 'border-gray-100 hover:border-blue-200']">
          <div class="flex items-start gap-4 flex-wrap">
            <div :class="['w-16 h-16 rounded-2xl flex flex-col items-center justify-center text-white shrink-0', rdv.statut === 'Annulé' ? 'bg-gray-400' : 'bg-blue-600']">
              <p class="text-xl font-extrabold leading-none">{{ new Date(rdv.date).getDate() }}</p>
              <p class="text-xs font-semibold uppercase">{{ new Date(rdv.date).toLocaleDateString('fr-FR', { month: 'short' }) }}</p>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <p class="font-extrabold text-gray-900">{{ rdv.type }}</p>
                <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', statutColor[rdv.statut]]">{{ rdv.statut }}</span>
                <span v-if="rdv.statut !== 'Annulé'" :class="['text-xs font-bold px-2 py-0.5 rounded-full', joursAvant(rdv.date) <= 3 ? 'bg-red-100 text-red-700' : joursAvant(rdv.date) <= 7 ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700']">
                  J-{{ joursAvant(rdv.date) }}
                </span>
              </div>
              <p class="text-sm text-gray-600">{{ rdv.medecin }} · {{ rdv.service }}</p>
              <div class="flex flex-wrap gap-3 mt-1 text-xs text-gray-500">
                <span>🕐 {{ rdv.heure }}</span>
                <span>📍 {{ rdv.lieu }}</span>
              </div>
              <div v-if="rdv.instructions" class="mt-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-800">
                ℹ️ {{ rdv.instructions }}
              </div>
            </div>
            <div v-if="rdv.statut !== 'Annulé'" class="flex gap-2 shrink-0">
              <button @click="setRappel(rdv)" class="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 text-xs font-semibold hover:bg-blue-100 transition-colors">
                📲 Rappel
              </button>
              <button @click="annulerRdv(rdv)" class="px-3 py-1.5 rounded-lg border border-red-200 text-red-600 text-xs font-semibold hover:bg-red-50 transition-colors">
                Annuler
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Historique -->
    <div>
      <h2 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Historique</h2>
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="table-header">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Type</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Médecin</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in historique" :key="h.id" class="table-row border-b border-gray-50">
              <td class="px-4 py-3 text-xs text-gray-600 font-mono">{{ h.date }} · {{ h.heure }}</td>
              <td class="px-4 py-3 text-xs font-medium text-gray-900">{{ h.type }}</td>
              <td class="px-4 py-3 text-xs text-gray-600">{{ h.medecin }}</td>
              <td class="px-4 py-3">
                <span :class="['text-xs font-bold px-2.5 py-1 rounded-full', statutColor[h.statut]]">{{ h.statut }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-box">
          <h3 class="text-lg font-extrabold text-gray-900 mb-5">Prendre un rendez-vous</h3>
          <form @submit.prevent="confirmerRdv" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Spécialité <span class="text-red-500">*</span></label>
              <select v-model="form.specialite" class="input-field" required>
                <option value="">Choisir une spécialité...</option>
                <option v-for="s in specialites" :key="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Motif <span class="text-red-500">*</span></label>
              <input v-model="form.motif" class="input-field" placeholder="Ex: Consultation de suivi..." required />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Date <span class="text-red-500">*</span></label>
                <input v-model="form.date" type="date" class="input-field" :min="new Date().toISOString().split('T')[0]" required />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Créneau <span class="text-red-500">*</span></label>
                <select v-model="form.heure" class="input-field" required>
                  <option value="">Choisir...</option>
                  <option v-for="c in creneaux" :key="c">{{ c }}</option>
                </select>
              </div>
            </div>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-800">
              ℹ️ Confirmation par SMS sous 24h ouvrées.
            </div>
            <div class="flex gap-3">
              <button type="button" @click="showModal = false" class="btn-secondary flex-1">Annuler</button>
              <button type="submit" class="btn-primary flex-1 justify-center">Confirmer la demande</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
