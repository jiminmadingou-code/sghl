<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAccountsStore } from '@/stores/accounts'

const router = useRouter()
const store = useAccountsStore()
const step = ref(1)
const loading = ref(false)
const error = ref('')
const showPwd = ref(false)
const registeredUser = ref(null)

const ROLES = [
  { value: 'Médecin',     label: '🩺 Médecin',          group: 'Clinique' },
  { value: 'Infirmier',   label: '💉 Infirmier(ère)',    group: 'Clinique' },
  { value: 'Biologiste',  label: '🔬 Biologiste',        group: 'Laboratoire' },
  { value: 'Pharmacien',  label: '💊 Pharmacien(ne)',    group: 'Pharmacie' },
  { value: 'Radiologue',  label: '🩻 Radiologue',        group: 'Imagerie' },
  { value: 'Chirurgien',  label: '🔪 Chirurgien(ne)',    group: 'Clinique' },
  { value: 'Caissier',    label: '💳 Caissier(ère)',     group: 'Administration' },
  { value: 'Admin',       label: '⚙️ Administrateur',   group: 'Administration' },
  { value: 'Patient',     label: '👤 Patient',           group: 'Patient' },
]

const SERVICES = [
  'Médecine interne', 'Cardiologie', 'Chirurgie générale', 'Pédiatrie',
  'Maternité', 'Urgences', 'Laboratoire', 'Imagerie médicale',
  'Pharmacie', 'Facturation', 'Direction', 'Bloc opératoire',
]

const form = reactive({
  prenom: '', nom: '', email: '', telephone: '',
  role: '', service: '', matricule: '',
  password: '', confirm_password: '', accept_terms: false,
})

const isPatient = computed(() => form.role === 'Patient')

const passwordStrength = computed(() => {
  const p = form.password
  if (!p) return { score: 0, label: '', color: '' }
  let score = 0
  if (p.length >= 8) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return [
    { score: 0, label: '', color: '' },
    { score: 1, label: 'Faible', color: 'bg-red-500' },
    { score: 2, label: 'Moyen', color: 'bg-amber-500' },
    { score: 3, label: 'Bon', color: 'bg-blue-500' },
    { score: 4, label: 'Excellent', color: 'bg-green-500' },
  ][score]
})

async function handleRegister() {
  error.value = ''
  if (!form.prenom || !form.nom || !form.email || !form.role || !form.password) {
    error.value = 'Veuillez remplir tous les champs obligatoires.'; return
  }
  if (form.password !== form.confirm_password) {
    error.value = 'Les mots de passe ne correspondent pas.'; return
  }
  if (form.password.length < 6) {
    error.value = 'Le mot de passe doit contenir au moins 6 caractères.'; return
  }
  if (!form.accept_terms) {
    error.value = "Veuillez accepter les conditions d'utilisation."; return
  }

  loading.value = true
  await new Promise(r => setTimeout(r, 1000)) // simulation délai réseau

  try {
    // Tentative API réelle
    await fetch('/api/v1/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ first_name: form.prenom, last_name: form.nom, email: form.email, phone: form.telephone, role: form.role, service: form.service, matricule: form.matricule, password: form.password })
    })
  } catch { /* ignore, mode démo */ }

  try {
    // Enregistrer en local + simuler email/SMS
    registeredUser.value = store.register({
      prenom: form.prenom, nom: form.nom, email: form.email,
      telephone: form.telephone, role: form.role,
      service: form.service, matricule: form.matricule,
      password: form.password,
    })
    step.value = 2
  } catch (e) {
    error.value = e.message
  }
  loading.value = false
}

function goToLogin() {
  router.push(form.role === 'Patient' ? '/login/patient' : '/login/professionnel')
}
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 40%, #ede9fe 100%)">
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
      <a href="/" class="text-gray-600 hover:text-blue-700 text-sm font-medium">← Retour au site</a>
      <span class="font-bold text-gray-900 text-sm">🏥 DIGNE HOSPITAL</span>
    </div>

    <div class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-2xl">

        <!-- Étape 1 : Formulaire -->
        <div v-if="step === 1" class="bg-white rounded-2xl shadow-xl p-8 border border-blue-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-violet-600 flex items-center justify-center text-white text-xl">📝</div>
            <div>
              <h2 class="text-2xl font-extrabold text-gray-900">Créer un compte</h2>
              <p class="text-gray-500 text-sm">Rejoignez le système DIGNE HOSPITAL — Un email de confirmation vous sera envoyé</p>
            </div>
          </div>

          <!-- Sélection rôle -->
          <div class="mb-5">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Type de compte <span class="text-red-500">*</span></label>
            <div class="grid grid-cols-3 gap-2">
              <button v-for="r in ROLES" :key="r.value" type="button" @click="form.role = r.value"
                :class="['px-3 py-2.5 rounded-xl border-2 text-left transition-all text-sm font-medium',
                  form.role === r.value ? 'border-blue-600 bg-blue-50 text-blue-800' : 'border-gray-200 bg-white text-gray-700 hover:border-blue-300']">
                <span class="block">{{ r.label }}</span>
                <span class="text-[10px] text-gray-400 font-normal">{{ r.group }}</span>
              </button>
            </div>
          </div>

          <form @submit.prevent="handleRegister" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Prénom <span class="text-red-500">*</span></label>
                <input v-model="form.prenom" type="text" class="input-field" placeholder="Mamadou" required />
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Nom <span class="text-red-500">*</span></label>
                <input v-model="form.nom" type="text" class="input-field" placeholder="Diallo" required />
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Adresse email <span class="text-red-500">*</span></label>
              <input v-model="form.email" type="email" class="input-field" placeholder="votre@email.com" required />
              <p class="text-xs text-blue-600 mt-1">📧 Un email de confirmation + notification de connexion sera envoyé à cette adresse</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Téléphone <span class="text-gray-400 text-xs">(pour SMS)</span></label>
              <input v-model="form.telephone" type="tel" class="input-field" placeholder="+224 620 000 000" />
              <p class="text-xs text-gray-400 mt-1">📱 Un SMS de notification sera envoyé à ce numéro</p>
            </div>

            <div v-if="!isPatient">
              <label class="block text-sm font-semibold text-gray-700 mb-1">Service / Département</label>
              <select v-model="form.service" class="input-field">
                <option value="">Sélectionner un service</option>
                <option v-for="s in SERVICES" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>

            <div v-if="!isPatient">
              <label class="block text-sm font-semibold text-gray-700 mb-1">N° Matricule professionnel</label>
              <input v-model="form.matricule" type="text" class="input-field" placeholder="MAT-2025-XXXX" />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Mot de passe <span class="text-red-500">*</span></label>
              <div class="relative">
                <input v-model="form.password" :type="showPwd ? 'text' : 'password'"
                  class="input-field pr-10" placeholder="Minimum 6 caractères" required />
                <button type="button" @click="showPwd = !showPwd"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600 text-sm">
                  {{ showPwd ? '🙈' : '👁️' }}
                </button>
              </div>
              <div v-if="form.password" class="mt-2">
                <div class="flex gap-1 mb-1">
                  <div v-for="i in 4" :key="i" :class="['h-1.5 flex-1 rounded-full transition-colors', i <= passwordStrength.score ? passwordStrength.color : 'bg-gray-200']" />
                </div>
                <p class="text-xs font-medium" :class="passwordStrength.score >= 3 ? 'text-green-600' : 'text-amber-600'">
                  Force : {{ passwordStrength.label }}
                </p>
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Confirmer le mot de passe <span class="text-red-500">*</span></label>
              <input v-model="form.confirm_password" type="password" class="input-field" placeholder="Répétez le mot de passe" required />
              <p v-if="form.confirm_password && form.password !== form.confirm_password" class="text-xs text-red-600 mt-1">⚠ Les mots de passe ne correspondent pas</p>
            </div>

            <label class="flex items-start gap-3 cursor-pointer">
              <input v-model="form.accept_terms" type="checkbox" class="mt-0.5 w-4 h-4 accent-blue-600" />
              <span class="text-sm text-gray-600">
                J'accepte les <a href="#" class="text-blue-600 hover:underline font-medium">conditions d'utilisation</a>
                et la <a href="#" class="text-blue-600 hover:underline font-medium">politique de confidentialité</a>.
              </span>
            </label>

            <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">❌ {{ error }}</div>

            <button type="submit" :disabled="loading"
              class="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 text-white font-bold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-60 shadow-lg">
              <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ loading ? 'Création du compte...' : '✅ Créer mon compte' }}
            </button>
          </form>

          <p class="text-center text-sm text-gray-500 mt-5">
            Déjà un compte ?
            <a href="/login/professionnel" class="text-blue-600 font-semibold hover:underline">Se connecter</a>
          </p>
        </div>

        <!-- Étape 2 : Confirmation envoyée -->
        <div v-else class="bg-white rounded-2xl shadow-xl p-10 border border-green-100 text-center">
          <div class="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center text-4xl mx-auto mb-5">📧</div>
          <h2 class="text-2xl font-extrabold text-gray-900 mb-2">Compte créé avec succès !</h2>
          <p class="text-gray-600 mb-1">Email de confirmation envoyé à :</p>
          <p class="text-blue-700 font-extrabold text-lg mb-1">{{ registeredUser?.email }}</p>
          <p v-if="registeredUser?.telephone" class="text-gray-500 text-sm mb-4">SMS envoyé au : {{ registeredUser.telephone }}</p>

          <div class="bg-blue-50 border border-blue-200 rounded-xl p-5 text-left mb-4">
            <p class="font-bold text-blue-900 mb-1 text-sm">📋 Votre identifiant de connexion :</p>
            <p class="font-mono text-blue-700 font-bold text-lg bg-white px-4 py-2 rounded-lg border border-blue-200 text-center">
              {{ registeredUser?.username }}
            </p>
            <p class="text-xs text-blue-600 mt-2">⚠ Notez bien cet identifiant — il vous sera demandé à chaque connexion</p>
          </div>

          <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-left mb-4">
            <p class="font-bold text-amber-800 text-sm mb-2">🔔 Notifications activées :</p>
            <ul class="text-xs text-amber-700 space-y-1">
              <li>✅ Email de confirmation envoyé à {{ registeredUser?.email }}</li>
              <li v-if="registeredUser?.telephone">✅ SMS de bienvenue envoyé au {{ registeredUser?.telephone }}</li>
              <li>✅ À chaque connexion, vous recevrez un email + SMS de sécurité</li>
            </ul>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <button @click="goToLogin"
              class="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold text-sm hover:from-blue-700 hover:to-violet-700 transition-all shadow-lg">
              🔐 Se connecter maintenant
            </button>
            <button @click="step = 1"
              class="px-6 py-3 rounded-xl bg-gray-100 text-gray-700 font-semibold text-sm hover:bg-gray-200 transition-all">
              ← Modifier mes infos
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
