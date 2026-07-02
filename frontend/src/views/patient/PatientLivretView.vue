<script setup>
import { ref } from 'vue'
import { downloadLivretPDF } from '@/services/pdf'

const activeSection = ref('bienvenue')

const user = (() => { try { return JSON.parse(localStorage.getItem('sghl_user') || '{}') } catch { return {} } })()
const patientName = user.full_name || user.prenom ? `${user.prenom || ''} ${user.nom || ''}`.trim() : 'Patient'

const sections = [
  { key: 'bienvenue',    label: 'Bienvenue',              icon: '🏥' },
  { key: 'pratique',     label: 'Infos pratiques',        icon: '📋' },
  { key: 'droits',       label: 'Droits & devoirs',       icon: '⚖️' },
  { key: 'visites',      label: 'Visites & hébergement',  icon: '👨‍👩‍👧' },
  { key: 'restauration', label: 'Restauration',           icon: '🍽️' },
  { key: 'securite',     label: 'Sécurité & confidentialité', icon: '🔒' },
  { key: 'sortie',       label: 'Votre sortie',           icon: '🚪' },
  { key: 'contacts',     label: 'Contacts utiles',        icon: '📞' },
]
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-2xl font-extrabold text-gray-900">Livret d'accueil patient</h1>
        <p class="text-sm text-gray-500 mt-0.5">Toutes les informations utiles pour votre séjour au DIGNE HOSPITAL</p>
      </div>
      <button @click="downloadLivretPDF(patientName)" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        Télécharger le livret PDF
      </button>
    </div>

    <div class="flex gap-5 flex-col lg:flex-row">

      <!-- Sommaire -->
      <div class="lg:w-56 shrink-0">
        <div class="bg-white rounded-2xl border border-gray-100 p-3 sticky top-4">
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wide px-2 mb-2">Sommaire</p>
          <div class="space-y-0.5">
            <button v-for="s in sections" :key="s.key" @click="activeSection = s.key"
              :class="['w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-left',
                activeSection === s.key ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700']">
              <span>{{ s.icon }}</span>
              <span class="truncate">{{ s.label }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Contenu -->
      <div class="flex-1 bg-white rounded-2xl border border-gray-100 p-6 space-y-6">

        <!-- Bienvenue -->
        <div v-if="activeSection === 'bienvenue'">
          <div class="bg-gradient-to-r from-blue-600 to-cyan-500 rounded-2xl p-6 text-white mb-6">
            <h2 class="text-xl font-extrabold mb-2">Bienvenue au DIGNE HOSPITAL</h2>
            <p class="text-blue-100 leading-relaxed text-sm">
              L'ensemble du personnel médical, soignant et administratif vous souhaite la bienvenue et met tout en œuvre pour assurer votre confort et la qualité de votre prise en charge.
            </p>
          </div>
          <div class="space-y-4">
            <div class="flex items-start gap-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
              <span class="text-2xl shrink-0">🎯</span>
              <div>
                <p class="font-bold text-gray-900 mb-1">Notre mission</p>
                <p class="text-sm text-gray-600 leading-relaxed">Assurer des soins de qualité, accessibles à tous, dans le respect de la dignité et des droits de chaque patient. Le DIGNE HOSPITAL est un établissement public de santé de référence en République de Guinée.</p>
              </div>
            </div>
            <div class="flex items-start gap-4 p-4 bg-green-50 rounded-xl border border-green-100">
              <span class="text-2xl shrink-0">✅</span>
              <div>
                <p class="font-bold text-gray-900 mb-1">Accréditation & qualité</p>
                <p class="text-sm text-gray-600">Établissement certifié selon les normes HAS. Démarche qualité continue pour améliorer votre prise en charge.</p>
              </div>
            </div>
            <div class="flex items-start gap-4 p-4 bg-violet-50 rounded-xl border border-violet-100">
              <span class="text-2xl shrink-0">📱</span>
              <div>
                <p class="font-bold text-gray-900 mb-1">Votre espace numérique</p>
                <p class="text-sm text-gray-600">Via ce portail, accédez à vos résultats, ordonnances, factures et communiquez avec votre équipe soignante 24h/24.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Infos pratiques -->
        <div v-if="activeSection === 'pratique'" class="space-y-4">
          <h2 class="text-lg font-extrabold text-gray-900">Informations pratiques</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-for="info in [
              { icon: '🕐', titre: 'Horaires d\'accueil', contenu: 'Lundi – Vendredi : 07h00 – 18h00\nSamedi : 08h00 – 13h00\nUrgences : 24h/24 – 7j/7' },
              { icon: '🅿️', titre: 'Stationnement', contenu: 'Parking gratuit disponible devant le bâtiment principal.\nAccès PMR réservé à l\'entrée principale.' },
              { icon: '📶', titre: 'Wi-Fi gratuit', contenu: 'Réseau : CHU-Patient\nMot de passe disponible à l\'accueil.\nUsage personnel uniquement.' },
              { icon: '💰', titre: 'Caisse & paiements', contenu: 'Lundi – Vendredi : 08h00 – 16h00\nPaiement en ligne disponible 24h/24\nOrange Money · MTN · Carte bancaire' },
              { icon: '📞', titre: 'Standard téléphonique', contenu: '+224 620 000 000\nDisponible 24h/24 pour les urgences.\nSecrétariats : 07h30 – 17h00' },
              { icon: '🏧', titre: 'Distributeur automatique', contenu: 'Disponible dans le hall principal (Bâtiment A) et au niveau de la cafétéria (Bâtiment B).' },
            ]" :key="info.titre" class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xl">{{ info.icon }}</span>
                <p class="font-bold text-gray-900 text-sm">{{ info.titre }}</p>
              </div>
              <p class="text-xs text-gray-600 leading-relaxed whitespace-pre-line">{{ info.contenu }}</p>
            </div>
          </div>
        </div>

        <!-- Droits & devoirs -->
        <div v-if="activeSection === 'droits'" class="space-y-5">
          <h2 class="text-lg font-extrabold text-gray-900">Vos droits & devoirs</h2>
          <div>
            <p class="text-sm font-bold text-blue-700 mb-3 flex items-center gap-2"><span>⚖️</span> Vos droits fondamentaux</p>
            <div class="space-y-2">
              <div v-for="droit in [
                'Droit à l\'information sur votre état de santé et les soins proposés',
                'Droit au consentement libre et éclairé avant tout acte médical',
                'Droit à la confidentialité et au secret médical',
                'Droit d\'accès à votre dossier médical (délai légal : 8 jours)',
                'Droit de désigner une personne de confiance',
                'Droit de refuser un traitement (après information des conséquences)',
                'Droit à la prise en charge de la douleur',
                'Droit à des soins palliatifs et à un accompagnement en fin de vie',
              ]" :key="droit" class="flex items-start gap-2.5 p-3 bg-blue-50 rounded-xl">
                <svg class="w-4 h-4 text-blue-600 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
                <p class="text-sm text-gray-700">{{ droit }}</p>
              </div>
            </div>
          </div>
          <div>
            <p class="text-sm font-bold text-amber-700 mb-3 flex items-center gap-2"><span>📌</span> Vos devoirs</p>
            <div class="space-y-2">
              <div v-for="devoir in [
                'Respecter le règlement intérieur de l\'établissement',
                'Fournir des informations exactes sur votre état de santé et vos antécédents',
                'Respecter le personnel soignant et les autres patients',
                'Respecter les horaires de visites et les consignes de sécurité',
                'Signaler tout changement dans votre état de santé',
                'Régler les frais de séjour selon les modalités convenues',
              ]" :key="devoir" class="flex items-start gap-2.5 p-3 bg-amber-50 rounded-xl">
                <span class="text-amber-600 shrink-0 mt-0.5 font-bold text-sm">•</span>
                <p class="text-sm text-gray-700">{{ devoir }}</p>
              </div>
            </div>
          </div>
          <div class="bg-violet-50 border border-violet-200 rounded-xl p-4">
            <p class="font-bold text-violet-800 text-sm mb-1">📋 Personne de confiance</p>
            <p class="text-sm text-gray-600">Vous pouvez désigner une personne de confiance (proche, médecin traitant) qui sera consultée si vous n'êtes pas en mesure d'exprimer votre volonté. Signalez-la à l'équipe soignante à votre admission.</p>
          </div>
        </div>

        <!-- Visites -->
        <div v-if="activeSection === 'visites'" class="space-y-4">
          <h2 class="text-lg font-extrabold text-gray-900">Visites & hébergement</h2>
          <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <p class="font-bold text-blue-800 mb-3">🕐 Horaires de visite</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div v-for="s in [
                { service: 'Médecine générale',  horaires: '12h00 – 14h00 · 17h00 – 20h00' },
                { service: 'Chirurgie',          horaires: '13h00 – 14h00 · 17h00 – 19h00' },
                { service: 'Maternité',          horaires: '10h00 – 12h00 · 15h00 – 19h00' },
                { service: 'Pédiatrie',          horaires: 'Parents : 24h/24 · Autres : 14h00 – 19h00' },
                { service: 'Réanimation / USI',  horaires: 'Sur autorisation médicale uniquement' },
                { service: 'Urgences',           horaires: 'Accès restreint — renseignements au 620 000 001' },
              ]" :key="s.service" class="p-3 bg-white rounded-xl border border-blue-100">
                <p class="text-xs font-bold text-gray-900">{{ s.service }}</p>
                <p class="text-xs text-blue-700 font-medium mt-0.5">{{ s.horaires }}</p>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p class="font-bold text-gray-900 text-sm mb-2">🛏 Chambre & équipements</p>
              <ul class="space-y-1 text-xs text-gray-600">
                <li>• Lit médicalisé réglable électriquement</li>
                <li>• Télévision (accès gratuit)</li>
                <li>• Wi-Fi gratuit (réseau CHU-Patient)</li>
                <li>• Salle de bain privative ou partagée</li>
                <li>• Appel infirmier disponible 24h/24</li>
              </ul>
            </div>
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p class="font-bold text-gray-900 text-sm mb-2">🧳 Ce que vous pouvez apporter</p>
              <ul class="space-y-1 text-xs text-gray-600">
                <li>✅ Affaires de toilette personnelles</li>
                <li>✅ Vêtements confortables</li>
                <li>✅ Livres, magazines</li>
                <li>❌ Objets de valeur (responsabilité non engagée)</li>
                <li>❌ Alcool, tabac, nourriture non autorisée</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Restauration -->
        <div v-if="activeSection === 'restauration'" class="space-y-4">
          <h2 class="text-lg font-extrabold text-gray-900">Restauration</h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div v-for="repas in [
              { nom: 'Petit-déjeuner', heure: '07h00 – 08h30', icon: '☕' },
              { nom: 'Déjeuner',       heure: '12h00 – 13h30', icon: '🍽️' },
              { nom: 'Dîner',          heure: '18h30 – 20h00', icon: '🌙' },
            ]" :key="repas.nom" class="p-4 bg-orange-50 border border-orange-100 rounded-xl text-center">
              <span class="text-3xl">{{ repas.icon }}</span>
              <p class="font-bold text-gray-900 mt-2 text-sm">{{ repas.nom }}</p>
              <p class="text-xs text-orange-700 font-semibold mt-0.5">{{ repas.heure }}</p>
            </div>
          </div>
          <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
            <p class="font-bold text-gray-900 text-sm mb-2">🥗 Régimes spéciaux</p>
            <p class="text-sm text-gray-600">Les régimes alimentaires spéciaux (diabétique, sans sel, végétarien, halal, allergie alimentaire) sont pris en charge. Signalez vos besoins à l'équipe soignante dès votre admission.</p>
          </div>
          <div class="p-4 bg-blue-50 rounded-xl border border-blue-100">
            <p class="font-bold text-gray-900 text-sm mb-1">☕ Cafétéria</p>
            <p class="text-sm text-gray-600">Ouverte du lundi au vendredi de 07h00 à 18h00, le samedi de 08h00 à 14h00. Accessible aux patients ambulatoires et aux visiteurs. Bâtiment B, rez-de-chaussée.</p>
          </div>
        </div>

        <!-- Sécurité -->
        <div v-if="activeSection === 'securite'" class="space-y-4">
          <h2 class="text-lg font-extrabold text-gray-900">Sécurité & confidentialité</h2>
          <div class="space-y-3">
            <div v-for="item in [
              { icon: '🔒', titre: 'Secret médical', desc: 'Toutes les informations vous concernant sont strictement confidentielles. Aucune information ne sera communiquée sans votre consentement explicite.' },
              { icon: '📁', titre: 'Dossier médical', desc: 'Votre dossier médical est sécurisé et chiffré (AES-256). Vous pouvez en demander une copie à tout moment. Délai légal de communication : 8 jours ouvrés.' },
              { icon: '🛡️', titre: 'Protection des données (RGPD)', desc: 'Vos données personnelles sont traitées conformément à la réglementation en vigueur. Vous disposez d\'un droit d\'accès, de rectification et d\'opposition.' },
              { icon: '📵', titre: 'Téléphones portables', desc: 'L\'utilisation des téléphones portables est autorisée dans les chambres. Elle est interdite dans les blocs opératoires, les salles de réveil et les unités de soins intensifs.' },
              { icon: '🚭', titre: 'Tabac & alcool', desc: 'L\'établissement est entièrement non-fumeur. Il est interdit de fumer dans l\'enceinte de l\'hôpital, y compris dans les espaces extérieurs.' },
            ]" :key="item.titre" class="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100">
              <span class="text-2xl shrink-0">{{ item.icon }}</span>
              <div>
                <p class="font-bold text-gray-900 text-sm mb-1">{{ item.titre }}</p>
                <p class="text-sm text-gray-600 leading-relaxed">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sortie -->
        <div v-if="activeSection === 'sortie'" class="space-y-4">
          <h2 class="text-lg font-extrabold text-gray-900">Votre sortie</h2>
          <div class="bg-green-50 border border-green-200 rounded-xl p-4">
            <p class="font-bold text-green-800 mb-2">📋 Checklist avant votre départ</p>
            <div class="space-y-2">
              <label v-for="item in [
                'Récupérer votre ordonnance de sortie',
                'Récupérer votre compte-rendu d\'hospitalisation',
                'Régler votre facture (ou vérifier la prise en charge assurance)',
                'Prendre rendez-vous de suivi si nécessaire',
                'Récupérer vos effets personnels',
                'Récupérer vos résultats d\'examens',
              ]" :key="item" class="flex items-center gap-2.5 cursor-pointer">
                <input type="checkbox" class="w-4 h-4 rounded accent-green-600" />
                <span class="text-sm text-gray-700">{{ item }}</span>
              </label>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="p-4 bg-blue-50 rounded-xl border border-blue-100">
              <p class="font-bold text-gray-900 text-sm mb-2">🕐 Heure de sortie</p>
              <p class="text-sm text-gray-600">La sortie s'effectue généralement avant <strong>11h00</strong>. En cas de sortie tardive, signalez-le à l'équipe soignante.</p>
            </div>
            <div class="p-4 bg-amber-50 rounded-xl border border-amber-100">
              <p class="font-bold text-gray-900 text-sm mb-2">🚗 Transport</p>
              <p class="text-sm text-gray-600">Si vous avez besoin d'un transport médicalisé (VSL, ambulance), signalez-le 24h à l'avance à l'équipe soignante.</p>
            </div>
          </div>
          <div class="p-4 bg-violet-50 rounded-xl border border-violet-100">
            <p class="font-bold text-gray-900 text-sm mb-1">📝 Questionnaire de satisfaction</p>
            <p class="text-sm text-gray-600 mb-3">Votre avis nous aide à améliorer la qualité de nos soins. Merci de prendre quelques minutes pour répondre à notre questionnaire.</p>
            <button class="px-4 py-2 rounded-xl bg-violet-600 text-white text-xs font-bold hover:bg-violet-700 transition-colors">
              Donner mon avis
            </button>
          </div>
        </div>

        <!-- Contacts -->
        <div v-if="activeSection === 'contacts'" class="space-y-4">
          <h2 class="text-lg font-extrabold text-gray-900">Contacts utiles</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <a v-for="c in [
              { service: 'Urgences',              numero: '+224 620 000 001', icon: '🚨', color: 'bg-red-50 border-red-200' },
              { service: 'Standard général',      numero: '+224 620 000 000', icon: '📞', color: 'bg-gray-50 border-gray-200' },
              { service: 'Secrétariat médical',   numero: '+224 620 000 010', icon: '📋', color: 'bg-blue-50 border-blue-200' },
              { service: 'Rendez-vous',           numero: '+224 620 000 004', icon: '📅', color: 'bg-green-50 border-green-200' },
              { service: 'Facturation / Caisse',  numero: '+224 620 000 005', icon: '💳', color: 'bg-amber-50 border-amber-200' },
              { service: 'Assistante sociale',    numero: '+224 620 000 020', icon: '🤝', color: 'bg-violet-50 border-violet-200' },
              { service: 'Médiation / Plaintes',  numero: '+224 620 000 030', icon: '⚖️', color: 'bg-orange-50 border-orange-200' },
              { service: 'Aumônerie',             numero: '+224 620 000 040', icon: '🕊️', color: 'bg-teal-50 border-teal-200' },
            ]" :key="c.service" :href="`tel:${c.numero.replace(/\s/g,'')}`"
              :class="['flex items-center gap-3 p-3.5 rounded-xl border hover:shadow-sm transition-all', c.color]">
              <span class="text-xl shrink-0">{{ c.icon }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-gray-900">{{ c.service }}</p>
                <p class="text-xs text-blue-600 font-semibold">{{ c.numero }}</p>
              </div>
            </a>
          </div>
          <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
            <p class="font-bold text-gray-900 text-sm mb-1">✉️ Email</p>
            <p class="text-sm text-blue-600 font-medium">contact@digne-hospital.gn</p>
            <p class="text-xs text-gray-500 mt-1">Réponse sous 48h ouvrées pour les demandes non urgentes.</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
