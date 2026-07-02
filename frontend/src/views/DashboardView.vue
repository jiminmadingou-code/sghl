# backend/core/settings.py

import os

# ... (tes variables d'environnement existantes)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'sghl_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# Ajoute 'rest_framework_simplejwt.token_blacklist' à INSTALLED_APPS si ce n'est pas fait
# pour le refresh token blacklist (sécurité)# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()# backend/core/crypto_utils.py
from cryptography.fernet import Fernet
import os

KEY = os.getenv('AES_ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { dashboardService } from '@/services/sghl'
import { useThemeStore } from '@/stores/theme'
import { useI18nStore } from '@/stores/i18n'

const theme = useThemeStore()
const i18n = useI18nStore()
const now = ref(new Date())
let tick = null
let autoRefreshTick = null
const lastRefresh = ref(new Date())
const secondsSinceRefresh = ref(0)

onMounted(() => {
  tick = setInterval(() => {
    now.value = new Date()
    secondsSinceRefresh.value = Math.floor((new Date() - lastRefresh.value) / 1000)
  }, 1000)
  autoRefreshTick = setInterval(() => loadData(true), 30000)
  loadData()
})
onUnmounted(() => { clearInterval(tick); clearInterval(autoRefreshTick) })

const loading = ref(true)
const stats = ref({ patients_totaux: 0, patients_hospitalises: 0, hospitalisations_actives: 0, taux_occupation: 0, examens_en_attente: 0, examens_a_valider: 0, alertes_stock: 0, chiffre_affaires_jour: 0, chiffre_affaires_mois: 0 })
const kpiHospit   = ref({ admissions: 0, sorties: 0, sejour_moyen_jours: 0, actives: 0 })
const kpiLabo     = ref({ examens_total: 0, valides: 0, en_cours: 0, temps_moyen_heures: 0 })
const kpiFinances = ref({ factures_total: 0, recette_totale: 0, en_attente_paiement: 0, taux_recouvrement: 0 })
const DEMO = {
  stats:    { patients_totaux: 248, patients_hospitalises: 87, hospitalisations_actives: 87, taux_occupation: 72.5, examens_en_attente: 12, examens_a_valider: 5, alertes_stock: 3, chiffre_affaires_jour: 1850000, chiffre_affaires_mois: 24500000 },
  hospit:   { admissions: 63, sorties: 58, sejour_moyen_jours: 4.2, actives: 87 },
  labo:     { examens_total: 312, valides: 287, en_cours: 25, temps_moyen_heures: 3.4 },
  finances: { factures_total: 142, recette_totale: 24500000, en_attente_paiement: 8200000, taux_recouvrement: 74.9 },
}

// ── Health check système ─────────────────────────────────────────────────────────────────
const sante = ref({ status: 'unknown', database: 'unknown', cache: 'unknown', version: '1.0', patients_total: 0, hospitalisations_actives: 0 })
const santeLoading = ref(false)

async function loadSante() {
  santeLoading.value = true
  try {
    const res = await dashboardService.sante()
    sante.value = res.data
  } catch {
    sante.value = { status: 'degraded', database: 'error', cache: 'error', version: '1.0', patients_total: 0, hospitalisations_actives: 0 }
  } finally { santeLoading.value = false }
}

async function loadData() {
  loading.value = true
  try {
    const [s, h, l, f] = await Promise.allSettled([
      dashboardService.summary(), dashboardService.kpiHospitalisations(),
      dashboardService.kpiLabo(), dashboardService.kpiFinances(),
    ])
    stats.value     = s.status === 'fulfilled' ? s.value.data : DEMO.stats
    kpiHospit.value = h.status === 'fulfilled' ? h.value.data : DEMO.hospit
    kpiLabo.value   = l.status === 'fulfilled' ? l.value.data : DEMO.labo
    kpiFinances.value = f.status === 'fulfilled' ? f.value.data : DEMO.finances
  } catch {
    stats.value = DEMO.stats; kpiHospit.value = DEMO.hospit
    kpiLabo.value = DEMO.labo; kpiFinances.value = DEMO.finances
  } finally { loading.value = false }
  loadSante()
}

const kpis = computed(() => [
  { label: "Patients hospitalisés", value: stats.value.patients_hospitalises, icon: '👥', iconBg: 'bg-blue-700',  trend: `${stats.value.patients_totaux} total`,  trendUp: true,  spark: [8,12,9,15,11,18,14,20,16,stats.value.patients_hospitalises] },
  { label: "Taux d'occupation",     value: `${(stats.value.taux_occupation||0).toFixed(1)}%`, icon: '🏥', iconBg: 'bg-cyan-600', trend: `${stats.value.hospitalisations_actives} lits`, trendUp: null, spark: [65,68,70,72,69,74,71,73,70,Math.round(stats.value.taux_occupation||72)] },
  { label: 'Examens en attente',    value: stats.value.examens_en_attente,  icon: '🔬', iconBg: 'bg-amber-500', trend: `${stats.value.examens_a_valider} à valider`, trendUp: false, spark: [5,8,6,10,7,9,11,8,10,stats.value.examens_en_attente] },
  { label: 'Recettes du jour',      value: `${((stats.value.chiffre_affaires_jour||0)/1000000).toFixed(2)} M GNF`, icon: '💳', iconBg: 'bg-green-600', trend: `${((stats.value.chiffre_affaires_mois||0)/1000000).toFixed(1)} M ce mois`, trendUp: true, spark: [900,1100,950,1300,1150,1400,1600,1500,1700,Math.round((stats.value.chiffre_affaires_jour||1850000)/1000)] },
])

const servicesOccupation = [
  { nom: 'Méd. interne', lits: 30, occupes: 26, couleur: '#1d4ed8' },
  { nom: 'Cardiologie',  lits: 20, occupes: 12, couleur: '#0891b2' },
  { nom: 'Maternité',    lits: 25, occupes: 23, couleur: '#ec4899' },
  { nom: 'Chirurgie',    lits: 20, occupes: 9,  couleur: '#f59e0b' },
  { nom: 'Pédiatrie',    lits: 15, occupes: 11, couleur: '#10b981' },
  { nom: 'Urgences',     lits: 10, occupes: 6,  couleur: '#ef4444' },
]

// Données graphes
const admissionsSemaine = [
  { j: 'Lun', val: 9 }, { j: 'Mar', val: 12 }, { j: 'Mer', val: 7 },
  { j: 'Jeu', val: 15 }, { j: 'Ven', val: 11 }, { j: 'Sam', val: 6 }, { j: 'Dim', val: 3 },
]
const recettes7j = [
  { j: 'Lun', val: 1200000 }, { j: 'Mar', val: 1850000 }, { j: 'Mer', val: 1400000 },
  { j: 'Jeu', val: 2100000 }, { j: 'Ven', val: 1750000 }, { j: 'Sam', val: 900000 }, { j: 'Dim', val: 600000 },
]
const examensParType = [
  { label: 'NFS', val: 87, color: '#1d4ed8' },
  { label: 'Glycémie', val: 65, color: '#0891b2' },
  { label: 'ECG', val: 34, color: '#7c3aed' },
  { label: 'Radio', val: 52, color: '#f59e0b' },
  { label: 'Autres', val: 74, color: '#10b981' },
]

// SVG helpers
const BAR_W = 400; const BAR_H = 120
function barMax(arr) { return Math.max(...arr.map(d => d.val), 1) }
function barX(i, total) { return i * (BAR_W / total) + (BAR_W / total) * 0.15 }
function barWidth(total) { return (BAR_W / total) * 0.7 }
function barY(v, max) { return BAR_H - Math.round((v / max) * (BAR_H - 20)) }
function barHeight(v, max) { return Math.round((v / max) * (BAR_H - 20)) }

// Ligne courbe recettes
function linePoints(arr, w, h) {
  const max = Math.max(...arr.map(d => d.val), 1)
  const step = w / (arr.length - 1)
  return arr.map((d, i) => `${i * step},${h - Math.round((d.val / max) * (h - 16)) - 8}`).join(' ')
}
function lineArea(arr, w, h) {
  const max = Math.max(...arr.map(d => d.val), 1)
  const step = w / (arr.length - 1)
  const pts = arr.map((d, i) => `${i * step},${h - Math.round((d.val / max) * (h - 16)) - 8}`).join(' ')
  return `M0,${h} L${pts.split(' ').map(p => p).join(' L')} L${w},${h} Z`
}

// Donut occupation par service
function donutDash(pct) { const c = 2 * Math.PI * 14; return `${pct/100*c} ${c}` }

const tauxOccupation = computed(() => Math.round(stats.value.taux_occupation || 0))
function sparkMax(arr) { return Math.max(...(arr || [1])) }
function sparkHeight(v, arr) { return Math.round((v / sparkMax(arr)) * 100) }

// Camembert examens
const PIE_R = 40; const PIE_CX = 50; const PIE_CY = 50
function pieSlices(data) {
  const total = data.reduce((s, d) => s + d.val, 0)
  let cumul = 0
  return data.map(d => {
    const pct = d.val / total
    const startAngle = cumul * 2 * Math.PI - Math.PI / 2
    cumul += pct
    const endAngle = cumul * 2 * Math.PI - Math.PI / 2
    const x1 = PIE_CX + PIE_R * Math.cos(startAngle)
    const y1 = PIE_CY + PIE_R * Math.sin(startAngle)
    const x2 = PIE_CX + PIE_R * Math.cos(endAngle)
    const y2 = PIE_CY + PIE_R * Math.sin(endAngle)
    const large = pct > 0.5 ? 1 : 0
    return { ...d, path: `M${PIE_CX},${PIE_CY} L${x1.toFixed(1)},${y1.toFixed(1)} A${PIE_R},${PIE_R} 0 ${large} 1 ${x2.toFixed(1)},${y2.toFixed(1)} Z`, pct: Math.round(pct * 100) }
  })
}
</script>

<template>
  <div class="space-y-5">

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      <span class="ml-3 text-gray-500 text-sm">Chargement...</span>
    </div>

    <template v-else>

      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div v-for="kpi in kpis" :key="kpi.label" class="stat-card p-5 card-hover">
          <div class="flex items-start justify-between mb-3">
            <div :class="['w-11 h-11 rounded-lg flex items-center justify-center text-white text-xl', kpi.iconBg]">{{ kpi.icon }}</div>
            <span :class="['text-xs font-semibold px-2 py-0.5 rounded-full', kpi.trendUp === true ? 'bg-green-50 text-green-700' : kpi.trendUp === false ? 'bg-red-50 text-red-700' : 'bg-gray-50 text-gray-600']">
              {{ kpi.trendUp === true ? '↑' : kpi.trendUp === false ? '↓' : '' }} {{ kpi.trend }}
            </span>
          </div>
          <p class="text-2xl font-extrabold text-gray-900 leading-tight">{{ kpi.value }}</p>
          <p class="text-xs text-gray-500 mt-0.5 mb-3">{{ kpi.label }}</p>
          <div class="sparkline">
            <div v-for="(v, i) in kpi.spark" :key="i" :class="['sparkline-bar', i === kpi.spark.length - 1 ? 'active' : '']" :style="{ height: sparkHeight(v, kpi.spark) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- KPIs secondaires -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="stat-card p-4 border-l-4 border-blue-500">
          <p class="text-xs text-gray-500 mb-1">Admissions (30j)</p>
          <p class="text-2xl font-extrabold text-blue-600">{{ kpiHospit.admissions }}</p>
          <p class="text-xs text-gray-400">Séjour moy. {{ kpiHospit.sejour_moyen_jours }}j</p>
        </div>
        <div class="stat-card p-4 border-l-4 border-violet-500">
          <p class="text-xs text-gray-500 mb-1">Examens labo (7j)</p>
          <p class="text-2xl font-extrabold text-violet-600">{{ kpiLabo.examens_total }}</p>
          <p class="text-xs text-gray-400">{{ kpiLabo.valides }} validés</p>
        </div>
        <div class="stat-card p-4 border-l-4 border-green-500">
          <p class="text-xs text-gray-500 mb-1">Recettes (30j)</p>
          <p class="text-xl font-extrabold text-green-600">{{ ((kpiFinances.recette_totale||0)/1000000).toFixed(1) }}M</p>
          <p class="text-xs text-gray-400">GNF encaissés</p>
        </div>
        <div class="stat-card p-4 border-l-4 border-amber-500">
          <p class="text-xs text-gray-500 mb-1">Taux recouvrement</p>
          <p class="text-2xl font-extrabold text-amber-600">{{ (kpiFinances.taux_recouvrement||0).toFixed(1) }}%</p>
          <p class="text-xs text-gray-400">{{ kpiFinances.factures_total }} factures</p>
        </div>
      </div>

      <!-- Alerte stock -->
      <div v-if="stats.alertes_stock > 0" class="alert-warning-banner flex items-center gap-3">
        <span class="text-amber-700 font-bold text-sm shrink-0">⚠ Alertes stock :</span>
        <span class="text-sm text-amber-800">{{ stats.alertes_stock }} médicament(s) en rupture ou sous le seuil d'alerte.</span>
        <RouterLink to="/dashboard/pharmacie" class="ml-auto text-xs font-bold text-amber-700 hover:underline shrink-0">Voir →</RouterLink>
      </div>

      <!-- GRAPHES — ligne 1 : Admissions (barres) + Recettes (ligne) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

        <!-- Graphe barres : Admissions semaine -->
        <div class="stat-card p-5">
          <p class="section-title mb-4">Admissions — 7 derniers jours</p>
          <svg viewBox="0 0 400 140" class="w-full" style="height:140px">
            <!-- Lignes de grille -->
            <line v-for="n in 4" :key="n" :x1="0" :y1="BAR_H - (n-1)*25" :x2="BAR_W" :y2="BAR_H - (n-1)*25" stroke="#e2eaf6" stroke-width="1"/>
            <!-- Barres -->
            <g v-for="(d, i) in admissionsSemaine" :key="d.j">
              <rect
                :x="barX(i, admissionsSemaine.length)"
                :y="barY(d.val, barMax(admissionsSemaine))"
                :width="barWidth(admissionsSemaine.length)"
                :height="barHeight(d.val, barMax(admissionsSemaine))"
                rx="4" fill="#2563eb" opacity="0.85"
              />
              <text :x="barX(i, admissionsSemaine.length) + barWidth(admissionsSemaine.length)/2" :y="barY(d.val, barMax(admissionsSemaine)) - 4" text-anchor="middle" font-size="10" fill="#1e3a8a" font-weight="700">{{ d.val }}</text>
              <text :x="barX(i, admissionsSemaine.length) + barWidth(admissionsSemaine.length)/2" :y="BAR_H + 14" text-anchor="middle" font-size="10" fill="#6b7280">{{ d.j }}</text>
            </g>
          </svg>
          <div class="flex items-center gap-2 mt-2">
            <div class="w-3 h-3 rounded bg-blue-600"></div>
            <span class="text-xs text-gray-500">Admissions par jour</span>
            <span class="ml-auto text-xs font-bold text-blue-700">Total : {{ admissionsSemaine.reduce((s,d)=>s+d.val,0) }}</span>
          </div>
        </div>

        <!-- Graphe ligne : Recettes 7j -->
        <div class="stat-card p-5">
          <p class="section-title mb-4">Recettes — 7 derniers jours (GNF)</p>
          <svg viewBox="0 0 400 140" class="w-full" style="height:140px">
            <defs>
              <linearGradient id="recGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#16a34a" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#16a34a" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <line v-for="n in 4" :key="n" x1="0" :y1="20 + (n-1)*26" x2="400" :y2="20 + (n-1)*26" stroke="#e2eaf6" stroke-width="1"/>
            <!-- Aire -->
            <path :d="lineArea(recettes7j, 400, BAR_H)" fill="url(#recGrad)"/>
            <!-- Ligne -->
            <polyline :points="linePoints(recettes7j, 400, BAR_H)" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
            <!-- Points -->
            <g v-for="(d, i) in recettes7j" :key="d.j">
              <circle :cx="i * (400/(recettes7j.length-1))" :cy="BAR_H - Math.round((d.val / barMax(recettes7j)) * (BAR_H-16)) - 8" r="4" fill="white" stroke="#16a34a" stroke-width="2"/>
              <text :x="i * (400/(recettes7j.length-1))" :y="BAR_H + 14" text-anchor="middle" font-size="10" fill="#6b7280">{{ d.j }}</text>
            </g>
          </svg>
          <div class="flex items-center gap-2 mt-2">
            <div class="w-3 h-3 rounded bg-green-600"></div>
            <span class="text-xs text-gray-500">Recettes journalières</span>
            <span class="ml-auto text-xs font-bold text-green-700">Moy. {{ (recettes7j.reduce((s,d)=>s+d.val,0)/recettes7j.length/1000000).toFixed(2) }} M/j</span>
          </div>
        </div>
      </div>

      <!-- GRAPHES — ligne 2 : Occupation lits + Camembert examens -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

        <!-- Occupation des lits par service -->
        <div class="stat-card p-5">
          <div class="flex items-center justify-between mb-4">
            <p class="section-title">Occupation des lits par service</p>
            <span :class="['text-sm font-bold px-3 py-1 rounded-full', tauxOccupation > 85 ? 'bg-red-100 text-red-700' : tauxOccupation > 70 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700']">{{ tauxOccupation }}% global</span>
          </div>
          <div class="progress-bar mb-4">
            <div class="progress-fill" :style="{ width: tauxOccupation + '%', background: tauxOccupation > 85 ? '#ef4444' : tauxOccupation > 70 ? '#f59e0b' : '#1d4ed8' }"></div>
          </div>
          <!-- Barres horizontales -->
          <div class="space-y-2.5">
            <div v-for="s in servicesOccupation" :key="s.nom" class="flex items-center gap-3">
              <span class="text-xs font-semibold text-gray-600 w-24 shrink-0 truncate">{{ s.nom }}</span>
              <div class="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                <div class="h-3 rounded-full transition-all duration-700" :style="{ width: Math.round(s.occupes/s.lits*100)+'%', background: s.couleur }"></div>
              </div>
              <span class="text-xs font-bold w-12 text-right shrink-0" :style="{ color: s.couleur }">{{ s.occupes }}/{{ s.lits }}</span>
              <span class="text-xs text-gray-400 w-8 shrink-0">{{ Math.round(s.occupes/s.lits*100) }}%</span>
            </div>
          </div>
        </div>

        <!-- Camembert examens par type -->
        <div class="stat-card p-5">
          <p class="section-title mb-4">Répartition des examens par type</p>
          <div class="flex items-center gap-6">
            <svg viewBox="0 0 100 100" class="w-36 h-36 shrink-0">
              <path v-for="s in pieSlices(examensParType)" :key="s.label" :d="s.path" :fill="s.color" stroke="white" stroke-width="1.5"/>
              <circle cx="50" cy="50" r="22" fill="white"/>
              <text x="50" y="47" text-anchor="middle" font-size="9" font-weight="700" fill="#1e3a8a">{{ examensParType.reduce((s,d)=>s+d.val,0) }}</text>
              <text x="50" y="57" text-anchor="middle" font-size="7" fill="#6b7280">examens</text>
            </svg>
            <div class="flex-1 space-y-2">
              <div v-for="s in pieSlices(examensParType)" :key="s.label" class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-sm shrink-0" :style="{ background: s.color }"></div>
                <span class="text-xs text-gray-600 flex-1">{{ s.label }}</span>
                <span class="text-xs font-bold" :style="{ color: s.color }">{{ s.val }}</span>
                <span class="text-xs text-gray-400">{{ s.pct }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- GRAPHE — Barres empilées : Labo workflow -->
      <div class="stat-card p-5">
        <p class="section-title mb-4">Pipeline laboratoire — Statuts en cours</p>
        <div class="flex items-end gap-4 overflow-x-auto pb-2">
          <div v-for="step in [
            { label: 'Commande',        val: 5,  color: '#dbeafe', text: '#1e40af' },
            { label: 'Prélèvement',     val: 8,  color: '#fde68a', text: '#92400e' },
            { label: 'Affectation',     val: 6,  color: '#fed7aa', text: '#9a3412' },
            { label: 'Saisie résultats',val: 11, color: '#ede9fe', text: '#5b21b6' },
            { label: 'Validé',          val: 18, color: '#bbf7d0', text: '#14532d' },
            { label: 'Publié',          val: 34, color: '#a7f3d0', text: '#065f46' },
          ]" :key="step.label" class="flex flex-col items-center gap-1.5 flex-1 min-w-[80px]">
            <span class="text-sm font-extrabold" :style="{ color: step.text }">{{ step.val }}</span>
            <div class="w-full rounded-t-lg transition-all duration-700" :style="{ height: Math.round(step.val/34*80)+'px', background: step.color, border: '1px solid rgba(0,0,0,0.06)' }"></div>
            <span class="text-[10px] text-gray-500 text-center leading-tight font-medium">{{ step.label }}</span>
          </div>
        </div>
      </div>

      <!-- Widget Health Check Système -->
      <div class="stat-card p-5">
        <div class="flex items-center justify-between mb-3">
          <p class="section-title">Statut système — <code class="text-xs bg-gray-100 px-1 rounded">/api/v1/sante/</code></p>
          <button @click="loadSante" :disabled="santeLoading"
            class="text-xs text-blue-600 hover:underline disabled:opacity-50 flex items-center gap-1">
            <span v-if="santeLoading" class="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></span>
            Actualiser
          </button>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 border">
            <span :class="['w-3 h-3 rounded-full shrink-0', sante.status === 'ok' ? 'bg-green-500' : sante.status === 'degraded' ? 'bg-amber-500' : 'bg-gray-400']"></span>
            <div>
              <p class="text-xs text-gray-500">API</p>
              <p class="text-sm font-bold" :class="sante.status === 'ok' ? 'text-green-700' : 'text-amber-700'">
                {{ sante.status === 'ok' ? 'Opérationnel' : sante.status === 'degraded' ? 'Dégradé' : 'Inconnu' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 border">
            <span :class="['w-3 h-3 rounded-full shrink-0', sante.database === 'ok' ? 'bg-green-500' : 'bg-red-500']"></span>
            <div>
              <p class="text-xs text-gray-500">Base de données</p>
              <p class="text-sm font-bold" :class="sante.database === 'ok' ? 'text-green-700' : 'text-red-700'">
                {{ sante.database === 'ok' ? 'Connectée' : 'Erreur' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 border">
            <span :class="['w-3 h-3 rounded-full shrink-0', sante.cache === 'ok' ? 'bg-green-500' : 'bg-amber-500']"></span>
            <div>
              <p class="text-xs text-gray-500">Cache Redis</p>
              <p class="text-sm font-bold" :class="sante.cache === 'ok' ? 'text-green-700' : 'text-amber-700'">
                {{ sante.cache === 'ok' ? 'Actif' : 'Inactif' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 border">
            <span class="w-3 h-3 rounded-full bg-blue-500 shrink-0"></span>
            <div>
              <p class="text-xs text-gray-500">Version API</p>
              <p class="text-sm font-bold text-blue-700">v{{ sante.version || '1.0' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Liens rapides modules -->
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <RouterLink v-for="m in [
          {path:'/dashboard/urgences',        icon:'🚨', label:'Urgences',    color:'bg-red-100 text-red-700'},
          {path:'/dashboard/laboratoire',     icon:'🔬', label:'Labo',        color:'bg-violet-100 text-violet-700'},
          {path:'/dashboard/imagerie',        icon:'🩻', label:'Imagerie',    color:'bg-blue-100 text-blue-700'},
          {path:'/dashboard/bloc-operatoire', icon:'🔪', label:'Bloc op.',    color:'bg-slate-100 text-slate-700'},
          {path:'/dashboard/maternite',       icon:'🤱', label:'Maternité',   color:'bg-pink-100 text-pink-700'},
          {path:'/dashboard/pharmacie',       icon:'💊', label:'Pharmacie',   color:'bg-green-100 text-green-700'},
          {path:'/dashboard/facturation',     icon:'💳', label:'Facturation', color:'bg-amber-100 text-amber-700'},
        ]" :key="m.path" :to="m.path"
          class="stat-card p-4 flex flex-col items-center gap-2 hover:shadow-md transition-all card-hover">
          <div :class="['w-10 h-10 rounded-xl flex items-center justify-center text-xl', m.color]">{{ m.icon }}</div>
          <p class="text-xs font-semibold text-gray-700 text-center">{{ m.label }}</p>
        </RouterLink>
      </div>

    </template>
  </div>
</template>
