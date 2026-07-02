<script setup>
import { ref } from 'vue'

const showAddModal = ref(false)
const formPartage = ref({ destinataire: '', type: '', duree: '30', documents: [] })

const partages = ref([
  {
    id: 1, destinataire: 'Dr. Koné Ibrahima', etablissement: 'Clinique Ambroise Paré', type: 'Médecin traitant',
    acces: ['Dossier médical complet', 'Résultats d\'examens', 'Ordonnances'],
    depuis: '2025-01-15', expire: '2025-12-31', statut: 'Actif', protocole: 'HL7 FHIR R4',
  },
  {
    id: 2, destinataire: 'Dr. Balde Fatoumata', etablissement: 'Centre de Santé Matam', type: 'Spécialiste',
    acces: ['Résultats d\'examens', 'Comptes-rendus imagerie'],
    depuis: '2025-05-01', expire: '2025-08-01', statut: 'Actif', protocole: 'HL7 FHIR R4',
  },
  {
    id: 3, destinataire: 'CHU de Dakar', etablissement: 'CHU de Dakar — Sénégal', type: 'Établissement partenaire',
    acces: ['Dossier médical complet'],
    depuis: '2025-03-10', expire: '2025-06-10', statut: 'Expiré', protocole: 'HL7 FHIR R4',
  },
])

const typesAcces = [
  'Dossier médical complet',
  'Résultats d\'examens biologiques',
  'Comptes-rendus imagerie',
  'Ordonnances & prescriptions',
  'Historique des hospitalisations',
  'Plan de soins',
]

const selectedDocs = ref([])

function toggleDoc(doc) {
  const idx = selectedDocs.value.indexOf(doc)
  if (idx === -1) selectedDocs.value.push(doc)
  else selectedDocs.value.splice(idx, 1)
}

function revoquer(id) {
  const p = partages.value.find(p => p.id === id)
  if (p) p.statut = 'Révoqué'
}

function ajouterPartage() {
  partages.value.unshift({
    id: Date.now(),
    destinataire: formPartage.value.destinataire,
    etablissement: 'À confirmer',
    type: formPartage.value.type,
    acces: [...selectedDocs.value],
    depuis: new Date().toISOString().split('T')[0],
    expire: new Date(Date.now() + formPartage.value.duree * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    statut: 'En attente',
    protocole: 'HL7 FHIR R4',
  })
  showAddModal.value = false
  selectedDocs.value = []
  formPartage.value = { destinataire: '', type: '', duree: '30', documents: [] }
}

const statutColor = { 'Actif': 'badge-success', 'Expiré': 'badge-warning', 'Révoqué': 'badge-danger', 'En attente': 'badge-info' }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Partage inter-établissements</h1>
        <p class="text-sm text-gray-500 mt-0.5">Gérez l'accès à votre dossier médical par d'autres professionnels de santé</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">+ Autoriser un accès</button>
    </div>

    <!-- Explication FHIR -->
    <div class="bg-gradient-to-r from-violet-600 to-blue-600 rounded-2xl p-5 text-white">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-2xl shrink-0">🔗</div>
        <div>
          <h2 class="font-extrabold text-lg mb-1">Interopérabilité HL7 FHIR R4</h2>
          <p class="text-blue-100 text-sm leading-relaxed">
            Votre dossier médical peut être partagé de manière sécurisée avec votre médecin traitant, des spécialistes ou d'autres établissements de santé, grâce au standard international HL7 FHIR. Vous gardez le contrôle total sur qui accède à vos données.
          </p>
          <div class="flex flex-wrap gap-2 mt-3">
            <span v-for="tag in ['HL7 FHIR R4', 'Chiffrement TLS', 'Consentement explicite', 'Révocable à tout moment']" :key="tag"
              class="text-xs bg-white/20 border border-white/30 px-3 py-1 rounded-full font-medium">
              ✓ {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Partages actifs -->
    <div>
      <h2 class="text-sm font-bold text-gray-700 uppercase tracking-wide mb-3">Accès autorisés ({{ partages.length }})</h2>
      <div class="space-y-3">
        <div v-for="p in partages" :key="p.id"
          :class="['bg-white rounded-2xl border-2 p-5 transition-all', p.statut === 'Actif' ? 'border-green-200' : p.statut === 'En attente' ? 'border-blue-200' : 'border-gray-200 opacity-70']">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div class="flex items-start gap-3">
              <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0', p.statut === 'Actif' ? 'bg-green-100' : 'bg-gray-100']">
                🏥
              </div>
              <div>
                <div class="flex items-center gap-2 flex-wrap mb-1">
                  <p class="font-extrabold text-gray-900">{{ p.destinataire }}</p>
                  <span :class="['text-xs font-bold px-2.5 py-0.5 rounded-full', statutColor[p.statut]]">{{ p.statut }}</span>
                  <span class="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full font-semibold">{{ p.protocole }}</span>
                </div>
                <p class="text-sm text-gray-600">{{ p.etablissement }} · {{ p.type }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Du {{ p.depuis }} au {{ p.expire }}</p>
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <span v-for="a in p.acces" :key="a" class="text-[10px] bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded-full font-medium">
                    {{ a }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex gap-2 shrink-0">
              <button v-if="p.statut === 'Actif'" @click="revoquer(p.id)"
                class="px-3 py-1.5 rounded-xl border border-red-200 text-red-600 text-xs font-semibold hover:bg-red-50 transition-colors">
                Révoquer
              </button>
              <button class="px-3 py-1.5 rounded-xl bg-gray-100 text-gray-600 text-xs font-semibold hover:bg-gray-200 transition-colors">
                Détails
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Journal des accès -->
    <div class="bg-white rounded-2xl border border-gray-100 p-5">
      <h2 class="font-bold text-gray-900 mb-4">Journal des accès récents</h2>
      <div class="space-y-2">
        <div v-for="log in [
          { date: '2025-06-11 14:32', action: 'Consultation dossier', par: 'Dr. Koné Ibrahima', ip: '196.168.x.x' },
          { date: '2025-06-10 09:15', action: 'Téléchargement résultats NFS', par: 'Dr. Koné Ibrahima', ip: '196.168.x.x' },
          { date: '2025-06-08 11:00', action: 'Consultation ordonnances', par: 'Dr. Balde Fatoumata', ip: '197.149.x.x' },
        ]" :key="log.date" class="flex items-center gap-4 p-3 rounded-xl bg-gray-50 text-xs">
          <span class="text-gray-400 font-mono shrink-0">{{ log.date }}</span>
          <span class="flex-1 font-medium text-gray-700">{{ log.action }}</span>
          <span class="text-violet-600 font-semibold shrink-0">{{ log.par }}</span>
          <span class="text-gray-400 shrink-0 hidden sm:inline">{{ log.ip }}</span>
        </div>
      </div>
    </div>

    <!-- Modal ajout partage -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-box modal-box-lg">
          <h3 class="text-lg font-extrabold text-gray-900 mb-1">Autoriser un accès à mon dossier</h3>
          <p class="text-sm text-gray-500 mb-5">Votre consentement est requis. Vous pouvez révoquer cet accès à tout moment.</p>
          <div class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Nom du professionnel / établissement <span class="text-red-500">*</span></label>
                <input v-model="formPartage.destinataire" class="input-field" placeholder="Dr. Nom ou Nom établissement" required />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Type d'accès</label>
                <select v-model="formPartage.type" class="input-field">
                  <option>Médecin traitant</option>
                  <option>Spécialiste</option>
                  <option>Établissement partenaire</option>
                  <option>Médecine de ville</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Durée d'accès</label>
                <select v-model="formPartage.duree" class="input-field">
                  <option value="7">7 jours</option>
                  <option value="30">30 jours</option>
                  <option value="90">3 mois</option>
                  <option value="365">1 an</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-2">Documents accessibles</label>
              <div class="grid grid-cols-2 gap-2">
                <label v-for="doc in typesAcces" :key="doc"
                  class="flex items-center gap-2 p-2.5 rounded-xl bg-gray-50 border border-gray-100 cursor-pointer hover:bg-blue-50 hover:border-blue-200 transition-colors">
                  <input type="checkbox" :value="doc" v-model="selectedDocs" class="accent-blue-600" />
                  <span class="text-xs font-medium text-gray-700">{{ doc }}</span>
                </label>
              </div>
            </div>
            <div class="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800">
              ⚠️ En autorisant cet accès, vous consentez explicitement au partage de vos données médicales avec le destinataire indiqué, conformément à la réglementation sur la protection des données de santé.
            </div>
          </div>
          <div class="flex gap-3 mt-5">
            <button @click="showAddModal = false" class="btn-secondary flex-1">Annuler</button>
            <button @click="ajouterPartage" class="flex-1 py-2.5 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition-colors">
              ✅ Autoriser l'accès
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
