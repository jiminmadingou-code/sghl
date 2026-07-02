<script setup>
import { ref, computed } from 'vue'

const activeTab = ref('testimonial')
const submitted = ref(false)

const form = ref({
  type: 'testimonial',
  rating: 5,
  titre: '',
  message: '',
  service: '',
  date_visite: '',
  pieces_jointes: [],
  anonyme: false,
})

const categories = [
  { key: 'accueil', label: 'Accueil & Accueil client', icon: '👋' },
  { key: 'soins', label: 'Qualité des soins', icon: '💉' },
  { key: 'proprete', label: 'Propreté & Hygiène', icon: '🧹' },
  { key: 'delais', label: 'Délais d\'attente', icon: '⏰' },
  { key: 'personnel', label: 'Comportement du personnel', icon: '👨‍⚕️' },
  { key: 'infrastructure', label: 'Infrastructure & Équipements', icon: '🏥' },
  { key: 'facturation', label: 'Facturation & Paiement', icon: '💳' },
  { key: 'autre', label: 'Autre', icon: '📝' },
]

const testimonials = ref([
  { id: 1, auteur: 'Mme. Bah Aissatou', date: '2025-06-08', rating: 5, categorie: 'Soins', message: 'Excellent accueil à la maternité. Le personnel est très professionnel et attentionné. Je recommande vivement ce CHU.', anonyme: false, reponse: { date: '2025-06-09', message: 'Nous vous remercions pour votre retour positif. Votre satisfaction est notre priorité.' } },
  { id: 2, auteur: 'Anonyme', date: '2025-06-05', rating: 3, categorie: 'Délais', message: 'Temps d\'attente un peu long au laboratoire. Le reste était correct.', anonyme: true, reponse: null },
  { id: 3, auteur: 'M. Koné Ibrahima', date: '2025-05-28', rating: 4, categorie: 'Accueil', message: 'Bon service dans l\'ensemble. L\'équipe cardiologie est très compétente.', anonyme: false, reponse: { date: '2025-05-29', message: 'Merci pour votre retour. Nous partagerons vos compliments à l\'équipe cardiologie.' } },
])

const averageRating = computed(() => {
  const total = testimonials.value.reduce((sum, t) => sum + t.rating, 0)
  return (total / testimonials.value.length).toFixed(1)
})

const ratingDistribution = computed(() => {
  const dist = [0, 0, 0, 0, 0]
  testimonials.value.forEach(t => dist[t.rating - 1]++)
  return dist
})

function submitForm() {
  if (!form.value.titre || !form.value.message) return
  
  testimonials.value.unshift({
    id: Date.now(),
    auteur: form.value.anonyme ? 'Anonyme' : 'Moi',
    date: new Date().toISOString().split('T')[0],
    rating: form.value.rating,
    categorie: categories.find(c => c.key === form.value.service)?.label || 'Autre',
    message: form.value.message,
    anonyme: form.value.anonyme,
    reponse: null,
  })
  
  submitted.value = true
  setTimeout(() => { submitted.value = false }, 5000)
  
  form.value = { type: 'testimonial', rating: 5, titre: '', message: '', service: '', date_visite: '', anonyme: false }
}

function submitComplaint() {
  if (!form.value.titre || !form.value.message) return
  
  testimonials.value.unshift({
    id: Date.now(),
    auteur: form.value.anonyme ? 'Anonyme' : 'Moi',
    date: new Date().toISOString().split('T')[0],
    rating: 1,
    categorie: 'Réclamation',
    message: `[RÉCLAMATION] ${form.value.titre}\n\n${form.value.message}`,
    anonyme: form.value.anonyme,
    reponse: { date: new Date().toISOString().split('T')[0], message: 'Votre réclamation a été enregistrée. Vous recevrez une réponse sous 48h.' },
  })
  
  submitted.value = true
  setTimeout(() => { submitted.value = false }, 5000)
  
  form.value = { type: 'testimonial', rating: 5, titre: '', message: '', service: '', date_visite: '', anonyme: false }
}

function handleFile(e) {
  form.value.pieces_jointes = Array.from(e.target.files).map(f => f.name)
}

const placeholderMessage = computed(() => {
  return activeTab.value === 'testimonial'
    ? 'Décrivez votre expérience, ce qui s\'est bien passé, ce qui pourrait être amélioré...'
    : 'Décrivez votre problème en détail, avec le maximum d\'informations utiles...'
})

const placeholderTitre = computed(() => {
  return activeTab.value === 'testimonial'
    ? 'Résumez votre expérience en quelques mots'
    : 'Décrivez brièvement votre problème'
})
</script>

<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Témoignage & Réclamation</h1>
        <p class="text-sm text-gray-500 mt-1">Votre avis nous aide à améliorer la qualité de nos soins</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="bg-amber-100 border border-amber-200 rounded-xl px-4 py-2 text-center">
          <p class="text-xs text-amber-700">Note moyenne</p>
          <p class="text-2xl font-extrabold text-amber-800">{{ averageRating }} ⭐</p>
        </div>
        <div class="bg-blue-100 border border-blue-200 rounded-xl px-4 py-2 text-center">
          <p class="text-xs text-blue-700">Avis</p>
          <p class="text-2xl font-extrabold text-blue-800">{{ testimonials.length }}</p>
        </div>
      </div>
    </div>

    <!-- Répartition des notes -->
    <div class="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 class="font-bold text-gray-900 mb-4">Répartition des notes</h3>
      <div class="space-y-2">
        <div v-for="i in 5" :key="i" class="flex items-center gap-3">
          <span class="text-sm text-gray-600 w-12">{{ 6 - i }} ⭐</span>
          <div class="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
            <div :style="{ width: `${(ratingDistribution[5 - i] / testimonials.length) * 100}%` }"
              class="h-full bg-gradient-to-r from-amber-400 to-amber-600 rounded-full transition-all"></div>
          </div>
          <span class="text-sm font-bold text-gray-700 w-8 text-right">{{ ratingDistribution[5 - i] }}</span>
        </div>
      </div>
    </div>

    <!-- Onglets -->
    <div class="bg-white rounded-2xl border border-gray-100 p-2 flex gap-2">
      <button @click="activeTab = 'testimonial'"
        :class="['flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all',
          activeTab === 'testimonial' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-blue-50']">
        ✍️ Déposer un témoignage
      </button>
      <button @click="activeTab = 'complaint'"
        :class="['flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all',
          activeTab === 'complaint' ? 'bg-red-600 text-white shadow-sm' : 'text-gray-600 hover:bg-red-50']">
        📢 Déposer une réclamation
      </button>
    </div>

    <!-- Formulaire -->
    <div v-if="!submitted" class="bg-white rounded-2xl border border-gray-100 p-6">
      <!-- Type de formulaire -->
      <div class="mb-6">
        <h3 class="font-bold text-gray-900 mb-1">{{ activeTab === 'testimonial' ? '✍️ Votre témoignage' : '📢 Votre réclamation' }}</h3>
        <p class="text-sm text-gray-500">{{ activeTab === 'testimonial' ? 'Partagez votre expérience avec nos services' : 'Signalez un problème ou une insatisfaction' }}</p>
      </div>

      <!-- Note -->
      <div class="mb-6">
        <label class="block text-sm font-semibold text-gray-700 mb-2">Votre note</label>
        <div class="flex gap-2">
          <button v-for="i in 5" :key="i" @click="form.rating = i"
            :class="['text-3xl transition-all hover:scale-110', i <= form.rating ? 'opacity-100' : 'opacity-30']">
            ⭐
          </button>
        </div>
      </div>

      <!-- Catégorie -->
      <div class="mb-6">
        <label class="block text-sm font-semibold text-gray-700 mb-2">Catégorie</label>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button v-for="cat in categories" :key="cat.key" @click="form.service = cat.key"
            :class="['flex items-center gap-2 p-3 rounded-xl border-2 text-xs font-semibold transition-all',
              form.service === cat.key ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 hover:border-blue-200']">
            <span>{{ cat.icon }}</span>
            <span class="truncate">{{ cat.label }}</span>
          </button>
        </div>
      </div>

      <!-- Titre -->
      <div class="mb-4">
        <label class="block text-sm font-semibold text-gray-700 mb-1">Titre {{ activeTab === 'complaint' ? '(obligatoire pour réclamation)' : '' }}</label>
        <input v-model="form.titre" type="text" class="input-field" :placeholder="placeholderTitre" />
      </div>

      <!-- Message -->
      <div class="mb-4">
        <label class="block text-sm font-semibold text-gray-700 mb-1">Message
          <span v-if="activeTab === 'complaint'" class="text-red-500">(obligatoire)</span>
        </label>
        <textarea v-model="form.message" class="input-field" rows="5" :placeholder="placeholderMessage" />
      </div>

      <!-- Date de visite -->
      <div class="mb-4">
        <label class="block text-sm font-semibold text-gray-700 mb-1">Date de visite / consultation</label>
        <input v-model="form.date_visite" type="date" class="input-field" />
      </div>

      <!-- Pièces jointes -->
      <div class="mb-4">
        <label class="block text-sm font-semibold text-gray-700 mb-1">Pièces jointes (optionnel)</label>
        <label class="flex items-center gap-3 p-4 border-2 border-dashed border-gray-200 rounded-xl cursor-pointer hover:border-blue-300 transition-colors">
          <span class="text-2xl">📎</span>
          <div class="flex-1">
            <p class="text-sm font-semibold text-gray-700">Cliquez pour ajouter des fichiers</p>
            <p class="text-xs text-gray-500">PDF, JPG, PNG (max 5 Mo par fichier)</p>
          </div>
          <input type="file" multiple accept=".pdf,.jpg,.jpeg,.png" class="hidden" @change="handleFile" />
        </label>
        <div v-if="form.pieces_jointes.length" class="mt-2 space-y-1">
          <div v-for="(file, i) in form.pieces_jointes" :key="i" class="flex items-center gap-2 text-xs text-blue-600">
            <span>✅</span>
            <span class="font-semibold">{{ file }}</span>
          </div>
        </div>
      </div>

      <!-- Anonyme -->
      <div class="mb-6 flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
        <div>
          <p class="text-sm font-bold text-gray-900">Déposer anonymement</p>
          <p class="text-xs text-gray-500">Votre identité ne sera pas révélée</p>
        </div>
        <button @click="form.anonyme = !form.anonyme"
          :class="['w-12 h-6 rounded-full transition-colors relative', form.anonyme ? 'bg-blue-600' : 'bg-gray-300']">
          <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform', form.anonyme ? 'translate-x-6' : 'translate-x-0.5']"></span>
        </button>
      </div>

      <!-- Avertissement -->
      <div :class="['p-4 rounded-xl text-sm', activeTab === 'testimonial' ? 'bg-blue-50 border border-blue-200 text-blue-800' : 'bg-red-50 border border-red-200 text-red-800']">
        <p class="font-bold mb-1">{{ activeTab === 'testimonial' ? 'ℹ️ Votre témoignage' : '⚠️ Votre réclamation' }}</p>
        <p class="text-xs leading-relaxed">
          {{ activeTab === 'testimonial'
            ? 'En déposant un témoignage, vous consentez à ce qu\'il soit affiché publiquement sur notre site. Votre avis aide les autres patients et nous améliore continuellement.'
            : 'En déposant une réclamation, vous vous engagez à fournir des informations factuelles. Votre réclamation sera traitée sous 48h par notre service qualité. Toute fausse déclaration peut entraîner le rejet de votre réclamation.'
          }}
        </p>
      </div>

      <!-- Bouton soumettre -->
      <button @click="activeTab === 'testimonial' ? submitForm() : submitComplaint()"
        :class="['w-full py-3 rounded-xl text-white font-bold text-sm transition-all mt-6',
          activeTab === 'testimonial' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-red-600 hover:bg-red-700']">
        {{ activeTab === 'testimonial' ? '✍️ Déposer mon témoignage' : '📢 Déposer ma réclamation' }}
      </button>
    </div>

    <!-- Succès -->
    <div v-else class="bg-green-50 border-2 border-green-300 rounded-2xl p-8 text-center">
      <span class="text-5xl block mb-4">✅</span>
      <h3 class="text-xl font-extrabold text-gray-900 mb-2">
        {{ activeTab === 'testimonial' ? 'Témoignage envoyé !' : 'Réclamation enregistrée !' }}
      </h3>
      <p class="text-gray-600">
        {{ activeTab === 'testimonial'
          ? 'Merci pour votre retour. Votre témoignage sera publié après validation.'
          : 'Votre réclamation a été enregistrée. Vous recevrez une réponse sous 48h.'
        }}
      </p>
    </div>

    <!-- Liste des avis -->
    <div class="space-y-4">
      <h2 class="text-lg font-extrabold text-gray-900">Derniers avis ({{ testimonials.length }})</h2>
      <div v-for="t in testimonials" :key="t.id"
        class="bg-white rounded-2xl border border-gray-100 p-5">
        <div class="flex items-start justify-between gap-4 mb-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white font-bold text-sm">
              {{ t.auteur[0] }}
            </div>
            <div>
              <p class="font-bold text-gray-900">{{ t.anonyme ? 'Anonyme' : t.auteur }}</p>
              <p class="text-xs text-gray-500">{{ t.date }} · {{ t.categorie }}</p>
            </div>
          </div>
          <div class="flex gap-0.5">
            <span v-for="i in 5" :key="i" :class="['text-lg', i <= t.rating ? 'text-amber-400' : 'text-gray-200']">⭐</span>
          </div>
        </div>
        <p class="text-sm text-gray-700 leading-relaxed">{{ t.message }}</p>
        
        <!-- Réponse -->
        <div v-if="t.reponse" class="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
          <p class="text-xs font-bold text-blue-700 mb-1">Réponse de l'établissement</p>
          <p class="text-sm text-gray-700">{{ t.reponse.message }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ t.reponse.date }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
