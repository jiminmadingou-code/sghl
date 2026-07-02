<script setup>
import { ref, computed } from 'vue'

const step = ref(1)
const totalSteps = 4
const submitted = ref(false)

const form = ref({
  // Étape 1 — Identité
  nom: 'Diallo', prenom: 'Mamadou', ddn: '1979-03-15', sexe: 'M',
  lieu_naissance: 'Conakry', nationalite: 'Guinéenne',
  telephone: '+224 620 000 001', email: 'mamadou.diallo@email.com',
  adresse: 'Quartier Ratoma, Conakry',
  // Étape 2 — Couverture sociale
  assurance: 'CNSS Guinée', numero_assurance: 'CNSS-2025-001234',
  tiers_payant: true, mutuelle: '', medecin_traitant: 'Dr. Camara Alpha',
  // Étape 3 — Motif & antécédents
  motif: 'Hospitalisation programmée — Chirurgie', service: 'Chirurgie générale',
  date_prevue: '2025-06-20', allergies: 'Pénicilline',
  antecedents: 'HTA, Diabète type 2', traitements_en_cours: 'Amlodipine 5mg, Metformine 500mg',
  // Étape 4 — Documents
  docs: { cni: null, assurance_doc: null, ordonnance: null, analyses: null },
})

const steps = [
  { num: 1, label: 'Identité',          icon: '👤' },
  { num: 2, label: 'Couverture sociale', icon: '🏦' },
  { num: 3, label: 'Motif & santé',     icon: '🩺' },
  { num: 4, label: 'Documents',         icon: '📎' },
]

const progress = computed(() => Math.round(((step.value - 1) / (totalSteps - 1)) * 100))

const docsList = [
  { key: 'cni',          label: 'Pièce d\'identité (CNI / Passeport)', required: true,  icon: '🪪' },
  { key: 'assurance_doc',label: 'Attestation d\'assurance maladie',    required: true,  icon: '🏦' },
  { key: 'ordonnance',   label: 'Ordonnance médicale (si applicable)', required: false, icon: '💊' },
  { key: 'analyses',     label: 'Résultats d\'examens récents',        required: false, icon: '🔬' },
]

function handleFile(key, e) {
  form.value.docs[key] = e.target.files[0]?.name || null
}

function nextStep() { if (step.value < totalSteps) step.value++ }
function prevStep() { if (step.value > 1) step.value-- }
function submit() { submitted.value = true }
</script>

<template>
  <div class="space-y-5">
    <div>
      <h1 class="text-2xl font-extrabold text-gray-900">Formalités d'admission en ligne</h1>
      <p class="text-sm text-gray-500 mt-0.5">Complétez votre dossier avant votre arrivée au CHU — Gain de temps garanti</p>
    </div>

    <!-- Succès -->
    <div v-if="submitted" class="bg-white rounded-2xl border-2 border-green-300 p-8 text-center">
      <div class="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center text-4xl mx-auto mb-4">✅</div>
      <h2 class="text-xl font-extrabold text-gray-900 mb-2">Dossier d'admission envoyé !</h2>
      <p class="text-gray-600 mb-4">Votre dossier a été transmis au service administratif du CHU. Vous recevrez une confirmation par SMS et email dans les 24h.</p>
      <div class="bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-800 mb-5">
        <p class="font-bold mb-1">📋 Récapitulatif</p>
        <p>Admission prévue le <strong>{{ form.date_prevue }}</strong> · Service : <strong>{{ form.service }}</strong></p>
        <p class="mt-1">Référence dossier : <strong class="font-mono">ADM-2025-{{ Math.floor(Math.random()*9000)+1000 }}</strong></p>
      </div>
      <div class="flex gap-3 justify-center">
        <button @click="submitted = false; step = 1" class="btn-secondary">Modifier le dossier</button>
        <button class="btn-primary">📄 Télécharger le récapitulatif</button>
      </div>
    </div>

    <template v-else>
      <!-- Stepper -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex items-center justify-between mb-3">
          <p class="text-sm font-bold text-gray-700">Étape {{ step }} sur {{ totalSteps }}</p>
          <p class="text-sm font-bold text-blue-600">{{ progress }}% complété</p>
        </div>
        <div class="progress-bar mb-4">
          <div class="progress-fill bg-blue-600" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="grid grid-cols-4 gap-2">
          <div v-for="s in steps" :key="s.num"
            :class="['flex flex-col items-center gap-1 p-2 rounded-xl transition-all',
              step === s.num ? 'bg-blue-50 border border-blue-200' :
              step > s.num  ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-100']">
            <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
              step === s.num ? 'bg-blue-600 text-white' :
              step > s.num  ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500']">
              {{ step > s.num ? '✓' : s.num }}
            </div>
            <p :class="['text-[10px] font-semibold text-center leading-tight',
              step === s.num ? 'text-blue-700' : step > s.num ? 'text-green-700' : 'text-gray-400']">
              {{ s.label }}
            </p>
          </div>
        </div>
      </div>

      <!-- Formulaire -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6">

        <!-- Étape 1 — Identité -->
        <div v-if="step === 1" class="space-y-4">
          <h2 class="font-extrabold text-gray-900 text-lg flex items-center gap-2">👤 Informations personnelles</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Prénom <span class="text-red-500">*</span></label>
              <input v-model="form.prenom" class="input-field" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Nom <span class="text-red-500">*</span></label>
              <input v-model="form.nom" class="input-field" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Date de naissance <span class="text-red-500">*</span></label>
              <input v-model="form.ddn" type="date" class="input-field" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Sexe <span class="text-red-500">*</span></label>
              <select v-model="form.sexe" class="input-field">
                <option value="M">Masculin</option>
                <option value="F">Féminin</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Lieu de naissance</label>
              <input v-model="form.lieu_naissance" class="input-field" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Nationalité</label>
              <input v-model="form.nationalite" class="input-field" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Téléphone <span class="text-red-500">*</span></label>
              <input v-model="form.telephone" class="input-field" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Email</label>
              <input v-model="form.email" type="email" class="input-field" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Adresse complète <span class="text-red-500">*</span></label>
              <input v-model="form.adresse" class="input-field" />
            </div>
          </div>
        </div>

        <!-- Étape 2 — Couverture sociale -->
        <div v-if="step === 2" class="space-y-4">
          <h2 class="font-extrabold text-gray-900 text-lg flex items-center gap-2">🏦 Couverture sociale & assurance</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Organisme d'assurance <span class="text-red-500">*</span></label>
              <select v-model="form.assurance" class="input-field">
                <option>CNSS Guinée</option>
                <option>Assurance privée</option>
                <option>Mutuelle</option>
                <option>Aucune couverture</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">N° d'assuré</label>
              <input v-model="form.numero_assurance" class="input-field" placeholder="CNSS-XXXX-XXXXXX" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Mutuelle complémentaire</label>
              <input v-model="form.mutuelle" class="input-field" placeholder="Nom de la mutuelle" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Médecin traitant</label>
              <input v-model="form.medecin_traitant" class="input-field" placeholder="Dr. ..." />
            </div>
          </div>
          <div class="flex items-center justify-between p-4 bg-blue-50 rounded-xl border border-blue-100">
            <div>
              <p class="text-sm font-bold text-gray-900">Tiers payant</p>
              <p class="text-xs text-gray-500">Votre assurance règle directement une partie des frais</p>
            </div>
            <button @click="form.tiers_payant = !form.tiers_payant"
              :class="['w-12 h-6 rounded-full transition-colors relative', form.tiers_payant ? 'bg-blue-600' : 'bg-gray-300']">
              <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform', form.tiers_payant ? 'translate-x-6' : 'translate-x-0.5']"></span>
            </button>
          </div>
        </div>

        <!-- Étape 3 — Motif & santé -->
        <div v-if="step === 3" class="space-y-4">
          <h2 class="font-extrabold text-gray-900 text-lg flex items-center gap-2">🩺 Motif d'admission & santé</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Motif d'hospitalisation <span class="text-red-500">*</span></label>
              <input v-model="form.motif" class="input-field" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Service concerné <span class="text-red-500">*</span></label>
              <select v-model="form.service" class="input-field">
                <option v-for="s in ['Médecine interne','Cardiologie','Chirurgie générale','Maternité','Pédiatrie','Neurologie','Orthopédie']" :key="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1">Date d'admission prévue <span class="text-red-500">*</span></label>
              <input v-model="form.date_prevue" type="date" class="input-field" required />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Allergies connues</label>
              <input v-model="form.allergies" class="input-field" placeholder="Ex: Pénicilline, Aspirine..." />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Antécédents médicaux</label>
              <textarea v-model="form.antecedents" class="input-field" rows="2" placeholder="HTA, Diabète, chirurgies antérieures..."></textarea>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Traitements en cours</label>
              <textarea v-model="form.traitements_en_cours" class="input-field" rows="2" placeholder="Médicaments, posologie..."></textarea>
            </div>
          </div>
        </div>

        <!-- Étape 4 — Documents -->
        <div v-if="step === 4" class="space-y-4">
          <h2 class="font-extrabold text-gray-900 text-lg flex items-center gap-2">📎 Pièces justificatives</h2>
          <p class="text-sm text-gray-500">Transmettez vos documents avant votre arrivée pour accélérer votre admission. Formats acceptés : PDF, JPG, PNG (max 5 Mo).</p>
          <div class="space-y-3">
            <div v-for="doc in docsList" :key="doc.key"
              :class="['p-4 rounded-xl border-2 border-dashed transition-all', form.docs[doc.key] ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50 hover:border-blue-300']">
              <div class="flex items-center gap-3">
                <span class="text-2xl shrink-0">{{ doc.icon }}</span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-bold text-gray-900">
                    {{ doc.label }}
                    <span v-if="doc.required" class="text-red-500 ml-1">*</span>
                    <span v-else class="text-xs text-gray-400 font-normal ml-1">(optionnel)</span>
                  </p>
                  <p v-if="form.docs[doc.key]" class="text-xs text-green-600 font-semibold mt-0.5">✅ {{ form.docs[doc.key] }}</p>
                  <p v-else class="text-xs text-gray-400 mt-0.5">Aucun fichier sélectionné</p>
                </div>
                <label :for="doc.key" class="px-3 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-semibold cursor-pointer hover:bg-blue-700 transition-colors shrink-0">
                  {{ form.docs[doc.key] ? 'Modifier' : 'Choisir' }}
                </label>
                <input :id="doc.key" type="file" accept=".pdf,.jpg,.jpeg,.png" class="hidden" @change="handleFile(doc.key, $event)" />
              </div>
            </div>
          </div>
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
            <p class="font-bold mb-1">ℹ️ Important</p>
            <p>Vos documents sont transmis de manière sécurisée et chiffrée. Ils seront consultés uniquement par le personnel administratif habilité.</p>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex items-center justify-between mt-6 pt-5 border-t border-gray-100">
          <button v-if="step > 1" @click="prevStep" class="btn-secondary">← Précédent</button>
          <div v-else></div>
          <button v-if="step < totalSteps" @click="nextStep" class="btn-primary">Suivant →</button>
          <button v-else @click="submit" class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-green-600 text-white font-bold text-sm hover:bg-green-700 transition-colors">
            ✅ Soumettre mon dossier
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
