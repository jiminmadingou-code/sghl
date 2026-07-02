<script setup>
import { ref, computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import { downloadFacturePDF } from '@/services/pdf'

const toast = useToastStore()
const showPayModal = ref(false)
const selectedFacture = ref(null)
const payForm = ref({ mode: 'momo', telephone: '', reference: '', nom_banque: '' })
const page = ref(1)
const perPage = 5

const assurances = ref([
  { id: 1, nom: 'CNSS Guinée', numero: 'CNSS-2025-001234', taux: 80, actif: true },
])

const factures = ref([
  { id: 'F-2025-006', date: '2025-06-10', type: 'Hospitalisation', detail: 'Séjour 3 jours — Médecine interne', montant: 2800000, paye: 1400000, statut: 'Partielle', assurance: 700000, assurance_nom: 'CNSS Guinée' },
  { id: 'F-2025-005', date: '2025-06-10', type: 'Examens',         detail: 'NFS + Glycémie',                   montant: 85000,   paye: 85000,   statut: 'Payée',     assurance: 0,      assurance_nom: '' },
  { id: 'F-2025-004', date: '2025-05-20', type: 'Consultation',    detail: 'Consultation cardiologie',          montant: 150000,  paye: 150000,  statut: 'Payée',     assurance: 75000,  assurance_nom: 'CNSS Guinée' },
  { id: 'F-2025-003', date: '2025-04-15', type: 'Pharmacie',       detail: 'Médicaments ordonnance',            montant: 45000,   paye: 0,       statut: 'En attente',assurance: 0,      assurance_nom: '' },
  { id: 'F-2025-002', date: '2025-03-10', type: 'Consultation',    detail: 'Consultation médecine interne',     montant: 120000,  paye: 120000,  statut: 'Payée',     assurance: 60000,  assurance_nom: 'CNSS Guinée' },
  { id: 'F-2025-001', date: '2025-02-05', type: 'Examens',         detail: 'Bilan lipidique complet',           montant: 95000,   paye: 95000,   statut: 'Payée',     assurance: 0,      assurance_nom: '' },
])

const totalPages = computed(() => Math.ceil(factures.value.length / perPage))
const facturesPaged = computed(() => factures.value.slice((page.value - 1) * perPage, page.value * perPage))
const totalDu = computed(() => factures.value.reduce((s, f) => s + (f.montant - f.paye), 0))
const totalPaye = computed(() => factures.value.reduce((s, f) => s + f.paye, 0))
const totalAssurance = computed(() => factures.value.reduce((s, f) => s + f.assurance, 0))

function fmt(n) { return n.toLocaleString('fr-FR') + ' GNF' }
function pct(f) { return Math.round((f.paye / f.montant) * 100) }

const modesPaiement = [
  { key: 'momo',        label: 'Orange Money',      icon: '🟠', desc: 'Paiement via Orange Money' },
  { key: 'airtel',      label: 'Airtel Money',       icon: '🔴', desc: 'Paiement via Airtel Money' },
  { key: 'banque',      label: 'Compte bancaire',    icon: '🏦', desc: 'Virement ou carte bancaire' },
  { key: 'presentiel',  label: 'En présentiel',      icon: '🏥', desc: 'Payer à la caisse du CHU' },
]

function openPay(f) {
  selectedFacture.value = f
  payForm.value = { mode: 'momo', telephone: '', reference: '', nom_banque: '' }
  showPayModal.value = true
}

function confirmerPaiement() {
  const f = selectedFacture.value
  if (!f) return

  if (payForm.value.mode === 'presentiel') {
    toast.info('Référence de paiement générée. Présentez-vous à la caisse du CHU avec la référence : ' + f.id)
    showPayModal.value = false
    return
  }

  if ((payForm.value.mode === 'momo' || payForm.value.mode === 'airtel') && !payForm.value.telephone) {
    toast.error('Veuillez saisir votre numéro de téléphone')
    return
  }

  f.paye = f.montant
  f.statut = 'Payée'
  showPayModal.value = false

  const modeLabel = modesPaiement.find(m => m.key === payForm.value.mode)?.label
  toast.success(`Paiement de ${fmt(f.montant)} confirmé via ${modeLabel} ✓ Reçu envoyé par SMS`)
}

function imprimerFacture(f) {
  downloadFacturePDF(f)
}

function telechargerPDF(f) {
  downloadFacturePDF(f)
}

const statutColor = { 'Payée': 'badge-success', 'Partielle': 'badge-warning', 'En attente': 'badge-danger' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Mes factures</h1>
        <p class="text-sm text-gray-500 mt-0.5">Consultez, réglez et imprimez vos factures</p>
      </div>
      <button @click="toast.info('Relevé de compte généré')" class="btn-secondary text-sm">
        📄 Relevé de compte
      </button>
    </div>

    <!-- Assurance maladie -->
    <div class="bg-white rounded-2xl border border-blue-100 p-5">
      <div class="flex items-center justify-between mb-3">
        <p class="font-bold text-gray-900 flex items-center gap-2">🏦 Couverture maladie</p>
        <button @click="toast.info('Ajout d\'assurance — contactez le secrétariat')" class="text-xs text-blue-600 font-semibold hover:underline">+ Ajouter</button>
      </div>
      <div v-for="a in assurances" :key="a.id"
        class="flex items-center gap-4 p-3 bg-blue-50 rounded-xl border border-blue-100">
        <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0">
          {{ a.nom.split(' ').map(w=>w[0]).join('').slice(0,2) }}
        </div>
        <div class="flex-1">
          <p class="font-bold text-gray-900 text-sm">{{ a.nom }}</p>
          <p class="text-xs text-gray-500">N° {{ a.numero }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm font-extrabold text-blue-700">{{ a.taux }}%</p>
          <p class="text-xs text-gray-400">prise en charge</p>
        </div>
        <span :class="['text-xs font-bold px-2.5 py-1 rounded-full', a.actif ? 'badge-success' : 'badge-danger']">
          {{ a.actif ? 'Active' : 'Inactive' }}
        </span>
      </div>
      <div v-if="!assurances.length" class="text-center py-4 text-gray-400 text-sm">
        Aucune assurance enregistrée
      </div>
    </div>

    <!-- Résumé financier -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-2xl border border-gray-100 p-5 card-hover">
        <div class="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center text-xl mb-3">💰</div>
        <p class="text-xl font-extrabold text-red-600">{{ fmt(totalDu) }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Solde restant à payer</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-5 card-hover">
        <div class="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center text-xl mb-3">✅</div>
        <p class="text-xl font-extrabold text-green-600">{{ fmt(totalPaye) }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Total réglé</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-5 card-hover">
        <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-xl mb-3">🏦</div>
        <p class="text-xl font-extrabold text-blue-600">{{ fmt(totalAssurance) }}</p>
        <p class="text-xs text-gray-500 mt-0.5">Pris en charge assurance</p>
      </div>
    </div>

    <!-- Alerte solde -->
    <div v-if="totalDu > 0" class="alert-warning-banner flex items-center justify-between gap-4 flex-wrap">
      <div class="flex items-center gap-3">
        <span class="text-amber-700 font-bold text-lg">⚠</span>
        <p class="text-sm text-amber-800">Vous avez <strong>{{ fmt(totalDu) }}</strong> en attente de règlement.</p>
      </div>
      <button @click="openPay(factures.find(f => f.statut !== 'Payée'))"
        class="px-4 py-2 rounded-lg bg-amber-600 text-white text-xs font-bold hover:bg-amber-700 transition-colors shrink-0">
        Payer maintenant
      </button>
    </div>

    <!-- Liste factures avec pagination -->
    <div class="space-y-3">
      <div v-for="f in facturesPaged" :key="f.id"
        class="bg-white rounded-2xl border border-gray-100 p-5 hover:border-blue-200 transition-colors">
        <div class="flex items-start justify-between gap-4 flex-wrap mb-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-lg shrink-0">💳</div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <p class="font-bold text-gray-900 font-mono text-sm">{{ f.id }}</p>
                <span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">{{ f.type }}</span>
                <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', statutColor[f.statut]]">{{ f.statut }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-0.5">{{ f.date }} · {{ f.detail }}</p>
              <p v-if="f.assurance_nom" class="text-xs text-blue-600 mt-0.5">🏦 {{ f.assurance_nom }} : {{ fmt(f.assurance) }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-lg font-extrabold text-gray-900">{{ fmt(f.montant) }}</p>
            <p class="text-xs text-green-600 font-semibold">Payé : {{ fmt(f.paye) }}</p>
            <p class="text-xs text-gray-400">Reste : {{ fmt(f.montant - f.paye) }}</p>
          </div>
        </div>

        <div class="progress-bar mb-3">
          <div class="progress-fill"
            :style="{ width: pct(f) + '%', background: f.statut === 'Payée' ? '#16a34a' : f.statut === 'Partielle' ? '#f59e0b' : '#ef4444' }">
          </div>
        </div>

        <div class="flex items-center justify-between flex-wrap gap-2">
          <p class="text-xs text-gray-400">{{ pct(f) }}% réglé</p>
          <div class="flex gap-2 flex-wrap">
            <button @click="telechargerPDF(f)"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 text-xs font-semibold hover:bg-gray-50 transition-colors">
              📄 PDF
            </button>
            <button @click="imprimerFacture(f)"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 text-xs font-semibold hover:bg-gray-50 transition-colors">
              🖨️ Imprimer
            </button>
            <button v-if="f.statut !== 'Payée'" @click="openPay(f)"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-600 text-white text-xs font-bold hover:bg-green-700 transition-colors">
              💳 Payer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2">
      <button @click="page = Math.max(1, page - 1)" :disabled="page === 1"
        class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors">
        ← Précédent
      </button>
      <div class="flex gap-1">
        <button v-for="p in totalPages" :key="p" @click="page = p"
          :class="['w-8 h-8 rounded-lg text-sm font-bold transition-colors',
            page === p ? 'bg-blue-700 text-white' : 'border border-gray-200 text-gray-600 hover:bg-gray-50']">
          {{ p }}
        </button>
      </div>
      <button @click="page = Math.min(totalPages, page + 1)" :disabled="page === totalPages"
        class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors">
        Suivant →
      </button>
    </div>

    <!-- Modal paiement -->
    <Teleport to="body">
      <div v-if="showPayModal" class="modal-overlay" @click.self="showPayModal = false">
        <div class="modal-box max-w-md">
          <h3 class="text-lg font-extrabold text-gray-900 mb-1">Paiement sécurisé</h3>
          <p class="text-sm text-gray-500 mb-5">{{ selectedFacture?.id }} · {{ selectedFacture?.detail }}</p>

          <!-- Montant -->
          <div class="bg-green-50 border border-green-200 rounded-xl p-4 mb-5">
            <p class="text-xs text-gray-500 mb-1">Montant à régler</p>
            <p class="text-2xl font-extrabold text-green-700">
              {{ selectedFacture ? fmt(selectedFacture.montant - selectedFacture.paye) : '' }}
            </p>
            <p v-if="selectedFacture?.assurance_nom" class="text-xs text-blue-600 mt-1">
              🏦 Dont {{ fmt(selectedFacture.assurance) }} pris en charge par {{ selectedFacture.assurance_nom }}
            </p>
          </div>

          <!-- Modes de paiement -->
          <div class="mb-5">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Mode de paiement</label>
            <div class="grid grid-cols-2 gap-2">
              <button v-for="m in modesPaiement" :key="m.key"
                @click="payForm.mode = m.key"
                :class="['flex items-center gap-2 p-3 rounded-xl border-2 text-left transition-all',
                  payForm.mode === m.key ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300']">
                <span class="text-xl shrink-0">{{ m.icon }}</span>
                <div>
                  <p class="text-xs font-bold text-gray-900">{{ m.label }}</p>
                  <p class="text-[10px] text-gray-500">{{ m.desc }}</p>
                </div>
              </button>
            </div>
          </div>

          <!-- Champs selon mode -->
          <div class="space-y-3 mb-5">
            <div v-if="payForm.mode === 'momo' || payForm.mode === 'airtel'">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Numéro de téléphone <span class="text-red-500">*</span></label>
              <input v-model="payForm.telephone" class="input-field" placeholder="+224 620 000 000" />
            </div>
            <div v-if="payForm.mode === 'banque'">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Nom de la banque</label>
              <input v-model="payForm.nom_banque" class="input-field" placeholder="Ex: Ecobank, BCRG..." />
              <label class="block text-xs font-semibold text-gray-700 mb-1 mt-2">Référence de virement</label>
              <input v-model="payForm.reference" class="input-field" placeholder="Référence bancaire" />
            </div>
            <div v-if="payForm.mode === 'presentiel'" class="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <p class="text-sm font-bold text-amber-800 mb-1">📍 Paiement à la caisse</p>
              <p class="text-xs text-amber-700">Présentez-vous à la caisse du DIGNE HOSPITAL avec votre numéro de facture <strong>{{ selectedFacture?.id }}</strong>.</p>
              <p class="text-xs text-amber-700 mt-1">Horaires : Lun–Ven 08h00–16h00</p>
            </div>
          </div>

          <!-- Sécurité -->
          <div class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 mb-5">
            <svg class="w-4 h-4 text-blue-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <span class="text-xs text-blue-700 font-medium">Paiement sécurisé · Reçu par SMS et email</span>
          </div>

          <div class="flex gap-3">
            <button @click="showPayModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="confirmerPaiement"
              class="flex-1 py-2.5 rounded-xl bg-green-600 text-white font-bold text-sm hover:bg-green-700 transition-colors">
              ✅ Confirmer
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
