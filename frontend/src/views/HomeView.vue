<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const menuOpen = ref(false)

const specialites = [
  { icon: '❤️', nom: 'Cardiologie',        desc: 'Maladies cardiovasculaires' },
  { icon: '🧠', nom: 'Neurologie',          desc: 'Système nerveux' },
  { icon: '🦴', nom: 'Orthopédie',          desc: 'Os, articulations, muscles' },
  { icon: '👶', nom: 'Pédiatrie',           desc: 'Soins de l\'enfant' },
  { icon: '🤰', nom: 'Maternité',           desc: 'Grossesse & accouchement' },
  { icon: '🔬', nom: 'Biologie médicale',   desc: 'Analyses & laboratoire' },
  { icon: '🫁', nom: 'Pneumologie',         desc: 'Maladies respiratoires' },
  { icon: '🩺', nom: 'Médecine interne',    desc: 'Pathologies complexes' },
  { icon: '🔪', nom: 'Chirurgie générale',  desc: 'Interventions chirurgicales' },
  { icon: '👁️', nom: 'Ophtalmologie',       desc: 'Maladies des yeux' },
  { icon: '🦷', nom: 'Stomatologie',        desc: 'Chirurgie maxillo-faciale' },
  { icon: '🧪', nom: 'Oncologie',           desc: 'Cancérologie' },
]

const actualites = [
  {
    date: '12 juin 2025',
    categorie: 'Organisation',
    titre: 'Ouverture du nouveau bloc opératoire',
    desc: 'Le CHU inaugure son nouveau bloc opératoire de 8 salles équipées des dernières technologies chirurgicales.',
    img: '🏗️',
  },
  {
    date: '05 juin 2025',
    categorie: 'Prévention',
    titre: 'Campagne de vaccination contre la méningite',
    desc: 'Du 10 au 20 juin, vaccination gratuite pour les enfants de 0 à 5 ans dans tous nos services de pédiatrie.',
    img: '💉',
  },
  {
    date: '28 mai 2025',
    categorie: 'Innovation',
    titre: 'Lancement du dossier patient numérique',
    desc: 'Le SGHL permet désormais aux patients de consulter leurs résultats et ordonnances depuis leur espace en ligne.',
    img: '💻',
  },
]

const contacts = [
  { service: 'Standard général',    numero: '+242 06 000 0000', icon: '📞' },
  { service: 'Urgences',            numero: '+242 06 000 0001', icon: '🚨' },
  { service: 'Maternité',           numero: '+242 06 000 0002', icon: '🤰' },
  { service: 'Laboratoire',         numero: '+242 06 000 0003', icon: '🔬' },
  { service: 'Rendez-vous',         numero: '+242 06 000 0004', icon: '📅' },
  { service: 'Facturation',         numero: '+242 06 000 0005', icon: '💳' },
]

const portails = [
  {
    key: 'patient',
    titre: 'Espace Patient',
    desc: 'Prenez rendez-vous, consultez vos résultats, téléchargez vos ordonnances et échangez avec votre médecin.',
    icon: '👤',
    couleur: 'from-blue-600 to-cyan-500',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    items: ['Prise de rendez-vous en ligne', 'Résultats d\'examens PDF', 'Messagerie sécurisée', 'Suivi des factures'],
    route: '/login/patient',
    btnClass: 'bg-blue-600 hover:bg-blue-700',
  },
  {
    key: 'professionnel',
    titre: 'Espace Professionnel',
    desc: 'Accédez aux dossiers patients, prescriptions, planning de garde et outils cliniques.',
    icon: '🩺',
    couleur: 'from-violet-600 to-purple-500',
    bg: 'bg-violet-50',
    border: 'border-violet-200',
    items: ['Dossiers patients complets', 'Prescriptions électroniques', 'Planning & gardes', 'Laboratoire (LIS)'],
    route: '/login/professionnel',
    btnClass: 'bg-violet-600 hover:bg-violet-700',
  },
  {
    key: 'admin',
    titre: 'Espace Administrateur',
    desc: 'Pilotez l\'établissement : RH, statistiques, gestion des lits, facturation et paramètres système.',
    icon: '⚙️',
    couleur: 'from-slate-700 to-slate-500',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    items: ['Tableau de bord KPIs', 'Gestion RH & planning', 'Facturation & finances', 'Paramètres système'],
    route: '/login/admin',
    btnClass: 'bg-slate-700 hover:bg-slate-800',
  },
]
</script>

<template>
  <div class="min-h-screen bg-white font-sans">

    <!-- ── BARRE URGENCES ── -->
    <div class="bg-red-600 text-white py-2 px-4">
      <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2 text-sm">
        <div class="flex items-center gap-4 flex-wrap">
          <span class="font-bold flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-white animate-pulse inline-block"></span>
            URGENCES 24h/24 — 7j/7
          </span>
          <a href="tel:+242060000001" class="font-extrabold text-base tracking-wide hover:underline">📞 +242 06 000 0001</a>
        </div>
        <div class="flex items-center gap-4 text-xs flex-wrap">
          <span>SAMU : <strong>15</strong></span>
          <span>Pompiers : <strong>18</strong></span>
          <span>Police : <strong>17</strong></span>
          <span>N° Vert : <strong>0800 000 000</strong></span>
        </div>
      </div>
    </div>

    <!-- ── HEADER ── -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">

        <!-- Logo -->
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-700 to-blue-600 flex items-center justify-center shrink-0">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div>
            <p class="font-extrabold text-gray-900 text-lg leading-tight">DIGNE HOSPITAL</p>
            <p class="text-xs text-gray-500">Centre Hospitalier Universitaire · SGHL</p>
          </div>
        </div>

        <!-- Nav desktop -->
        <nav class="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
          <a href="#specialites" class="hover:text-violet-700 transition-colors">Spécialités</a>
          <a href="#portails" class="hover:text-violet-700 transition-colors">Accès portails</a>
          <a href="#actualites" class="hover:text-violet-700 transition-colors">Actualités</a>
          <a href="#contact" class="hover:text-violet-700 transition-colors">Contact</a>
        </nav>

        <!-- CTA buttons -->
        <div class="hidden md:flex items-center gap-2">
          <RouterLink to="/login/patient"
            class="px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors">
            Espace Patient
          </RouterLink>
          <RouterLink to="/login/professionnel"
            class="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-semibold hover:bg-violet-700 transition-colors">
            Espace Pro
          </RouterLink>
        </div>

        <!-- Burger mobile -->
        <button @click="menuOpen = !menuOpen" class="md:hidden p-2 rounded-lg hover:bg-gray-100">
          <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>

      <!-- Mobile menu -->
      <div v-if="menuOpen" class="md:hidden border-t border-gray-100 bg-white px-4 py-3 space-y-2">
        <a href="#specialites" class="block py-2 text-sm font-medium text-gray-700" @click="menuOpen=false">Spécialités</a>
        <a href="#portails" class="block py-2 text-sm font-medium text-gray-700" @click="menuOpen=false">Accès portails</a>
        <a href="#actualites" class="block py-2 text-sm font-medium text-gray-700" @click="menuOpen=false">Actualités</a>
        <a href="#contact" class="block py-2 text-sm font-medium text-gray-700" @click="menuOpen=false">Contact</a>
        <div class="flex gap-2 pt-2">
          <RouterLink to="/login/patient" class="flex-1 text-center py-2 rounded-xl bg-blue-600 text-white text-sm font-semibold">Patient</RouterLink>
          <RouterLink to="/login/professionnel" class="flex-1 text-center py-2 rounded-xl bg-violet-600 text-white text-sm font-semibold">Professionnel</RouterLink>
        </div>
      </div>
    </header>

    <!-- ── HERO ── -->
    <section class="relative overflow-hidden" style="background: linear-gradient(135deg, #1e1b4b 0%, #3b0764 40%, #1e40af 100%)">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-10 left-10 w-72 h-72 rounded-full bg-white blur-3xl"></div>
        <div class="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-blue-300 blur-3xl"></div>
      </div>
      <div class="relative max-w-7xl mx-auto px-4 py-20 md:py-28">
        <div class="max-w-3xl">
          <div class="inline-flex items-center gap-2 bg-white/15 border border-white/20 rounded-full px-4 py-1.5 text-white text-sm font-medium mb-6">
            <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            Établissement public de santé · Accrédité HAS
          </div>
          <h1 class="text-4xl md:text-5xl font-extrabold text-white leading-tight mb-4">
            Votre santé,<br>
            <span class="text-blue-300">notre priorité</span>
          </h1>
          <p class="text-blue-100 text-lg leading-relaxed mb-8 max-w-xl">
            Le DIGNE HOSPITAL vous accompagne à chaque étape de votre parcours de soins.
            Prenez rendez-vous, consultez vos résultats et gérez vos démarches en ligne.
          </p>
          <div class="flex flex-wrap gap-3">
            <RouterLink to="/login/patient"
              class="flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-violet-800 font-bold text-sm hover:bg-blue-50 transition-all shadow-lg">
              👤 Espace Patient
            </RouterLink>
            <a href="#portails"
              class="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/15 border border-white/30 text-white font-semibold text-sm hover:bg-white/25 transition-all">
              🩺 Espace Professionnel
            </a>
          </div>
        </div>
      </div>

      <!-- Stats band -->
      <div class="relative bg-white/10 border-t border-white/10 backdrop-blur-sm">
        <div class="max-w-7xl mx-auto px-4 py-5 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="s in [
            { v: '120', l: 'Lits disponibles' },
            { v: '12', l: 'Spécialités médicales' },
            { v: '350+', l: 'Professionnels de santé' },
            { v: '24/7', l: 'Urgences ouvertes' },
          ]" :key="s.l" class="text-center text-white">
            <p class="text-2xl font-extrabold">{{ s.v }}</p>
            <p class="text-blue-200 text-xs mt-0.5">{{ s.l }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── 3 PORTAILS ── -->
    <section id="portails" class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4">
        <div class="text-center mb-10">
          <h2 class="text-3xl font-extrabold text-gray-900 mb-2">Accédez à votre espace</h2>
          <p class="text-gray-500">Trois portails distincts selon votre profil</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="p in portails" :key="p.key"
            :class="['rounded-2xl border-2 p-6 flex flex-col transition-all hover:-translate-y-1 hover:shadow-xl', p.bg, p.border]">
            <!-- Header -->
            <div :class="['w-14 h-14 rounded-2xl bg-gradient-to-br flex items-center justify-center text-white text-2xl mb-4', p.couleur]">
              {{ p.icon }}
            </div>
            <h3 class="text-xl font-extrabold text-gray-900 mb-2">{{ p.titre }}</h3>
            <p class="text-gray-600 text-sm leading-relaxed mb-4">{{ p.desc }}</p>
            <!-- Features list -->
            <ul class="space-y-2 mb-6 flex-1">
              <li v-for="item in p.items" :key="item" class="flex items-center gap-2 text-sm text-gray-700">
                <svg class="w-4 h-4 text-green-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
                {{ item }}
              </li>
            </ul>
            <RouterLink :to="p.route"
              :class="['w-full text-center py-3 rounded-xl text-white font-bold text-sm transition-colors', p.btnClass]">
              Accéder → {{ p.titre }}
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- ── SPÉCIALITÉS ── -->
    <section id="specialites" class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4">
        <div class="text-center mb-10">
          <h2 class="text-3xl font-extrabold text-gray-900 mb-2">Nos spécialités médicales</h2>
          <p class="text-gray-500">Une prise en charge complète dans toutes les disciplines</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="s in specialites" :key="s.nom"
            class="flex items-center gap-3 p-4 rounded-xl border border-gray-100 hover:border-violet-200 hover:bg-violet-50 transition-all cursor-pointer group">
            <span class="text-2xl shrink-0">{{ s.icon }}</span>
            <div>
              <p class="font-semibold text-gray-900 text-sm group-hover:text-violet-700 transition-colors">{{ s.nom }}</p>
              <p class="text-xs text-gray-500">{{ s.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── ACTUALITÉS ── -->
    <section id="actualites" class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between mb-10">
          <div>
            <h2 class="text-3xl font-extrabold text-gray-900 mb-1">Actualités</h2>
            <p class="text-gray-500">Informations et événements de l'établissement</p>
          </div>
          <button class="text-sm font-semibold text-violet-600 hover:underline hidden sm:block">Toutes les actualités →</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="a in actualites" :key="a.titre"
            class="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg transition-all group">
            <div class="h-36 bg-gradient-to-br from-violet-100 to-blue-100 flex items-center justify-center text-6xl">
              {{ a.img }}
            </div>
            <div class="p-5">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-violet-100 text-violet-700">{{ a.categorie }}</span>
                <span class="text-xs text-gray-400">{{ a.date }}</span>
              </div>
              <h3 class="font-bold text-gray-900 mb-2 group-hover:text-violet-700 transition-colors">{{ a.titre }}</h3>
              <p class="text-sm text-gray-600 leading-relaxed">{{ a.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CONTACT & ACCÈS ── -->
    <section id="contact" class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4">
        <div class="text-center mb-10">
          <h2 class="text-3xl font-extrabold text-gray-900 mb-2">Contact & Accès</h2>
          <p class="text-gray-500">Retrouvez-nous facilement</p>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

          <!-- Contacts -->
          <div>
            <h3 class="font-bold text-gray-900 mb-4 text-lg">Numéros utiles</h3>
            <div class="space-y-3">
              <a v-for="c in contacts" :key="c.service" :href="`tel:${c.numero.replace(/\s/g,'')}`"
                class="flex items-center gap-4 p-4 rounded-xl border border-gray-100 hover:border-violet-200 hover:bg-violet-50 transition-all group">
                <span class="text-2xl shrink-0">{{ c.icon }}</span>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 text-sm group-hover:text-violet-700">{{ c.service }}</p>
                  <p class="text-violet-600 font-bold text-sm">{{ c.numero }}</p>
                </div>
                <svg class="w-4 h-4 text-gray-300 group-hover:text-violet-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </a>
            </div>
          </div>

          <!-- Adresse & plan -->
          <div>
            <h3 class="font-bold text-gray-900 mb-4 text-lg">Plan d'accès</h3>
            <div class="rounded-2xl border border-gray-200 overflow-hidden">
              <!-- Carte interactive Pointe-Noire -->
              <div class="h-48 relative overflow-hidden bg-gradient-to-br from-emerald-50 to-blue-100">
                <iframe
                  src="https://www.openstreetmap.org/export/embed.html?bbox=11.8200%2C-4.8000%2C11.8800%2C-4.7500&layer=mapnik&marker=-4.7761%2C11.8635"
                  class="w-full h-full border-0"
                  title="Carte Pointe-Noire, Congo"
                  loading="lazy"
                ></iframe>
                <div class="absolute bottom-2 right-2 bg-white/90 text-xs text-gray-600 px-2 py-1 rounded-lg font-medium shadow">
                  📍 Pointe-Noire, Congo
                </div>
              </div>
              <div class="p-5 space-y-3">
                <div class="flex items-start gap-3">
                  <span class="text-xl shrink-0 mt-0.5">📍</span>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">DIGNE HOSPITAL</p>
                    <p class="text-gray-600 text-sm">Avenue Charles de Gaulle<br>Pointe-Noire, République du Congo</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xl shrink-0">📞</span>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">Téléphone</p>
                    <p class="text-violet-600 text-sm font-bold">+242 06 000 0000</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xl shrink-0">🕐</span>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">Horaires d'accueil</p>
                    <p class="text-gray-600 text-sm">Lun–Ven : 07h00 – 18h00 · Urgences : 24h/24</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xl shrink-0">✉️</span>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">Email</p>
                    <p class="text-violet-600 text-sm font-medium">contact@digne-hospital.cg</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── FOOTER ── -->
    <footer class="bg-gray-900 text-gray-400 py-10">
      <div class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div class="md:col-span-2">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-xl bg-violet-600 flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
              </div>
              <div>
                <p class="text-white font-bold">DIGNE HOSPITAL</p>
                <p class="text-xs text-gray-500">Système SGHL v2.0</p>
              </div>
            </div>
            <p class="text-sm leading-relaxed">Établissement public de santé au service de la population congolaise. Soins de qualité, accessibles à tous.</p>
          </div>
          <div>
            <p class="text-white font-semibold mb-3 text-sm">Accès rapide</p>
            <ul class="space-y-2 text-sm">
              <li><RouterLink to="/login/patient" class="hover:text-white transition-colors">Espace Patient</RouterLink></li>
              <li><RouterLink to="/login/professionnel" class="hover:text-white transition-colors">Espace Professionnel</RouterLink></li>
              <li><RouterLink to="/login/admin" class="hover:text-white transition-colors">Espace Administrateur</RouterLink></li>
            </ul>
          </div>
          <div>
            <p class="text-white font-semibold mb-3 text-sm">Informations légales</p>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="hover:text-white transition-colors">Mentions légales</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Politique de confidentialité</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Charte RGPD</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Accessibilité</a></li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-800 pt-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
          <p>© 2025 DIGNE HOSPITAL · Tous droits réservés · Développé par NLP-Core-Team</p>
          <p>SGHL — Système de Gestion Hospitalière et de Laboratoire</p>
        </div>
      </div>
    </footer>

  </div>
</template>
