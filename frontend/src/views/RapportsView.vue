<script setup>
import { ref, onMounted } from 'vue'
import { dashboardService, laboService, pharmacieService, facturationService } from '@/services/sghl'

const periode = ref('mois')
const loading = ref(true)

const kpis = ref([
  { label: 'Consultations', value: 0, variation: '+12%', icon: '🩺', color: 'bg-violet-100' },
  { label: 'Hospitalisations', value: 0, variation: '+5%', icon: '🏥', color: 'bg-blue-100' },
  { label: 'Examens réalisés', value: 0, variation: '+18%', icon: '🔬', color: 'bg-green-100' },
  { label: 'Recettes totales', value: '0 GNF', variation: '+9%', icon: '💳', color: 'bg-amber-100' },
])

const topDiagnostics = ref([
  { code: 'B54', libelle: 'Paludisme', count: 87, pct: 78 },
  { code: 'I10', libelle: 'HTA essentielle', count: 54, pct: 48 },
  { code: 'E11', libelle: 'Diabète type 2', count: 41, pct: 37 },
  { code: 'J06', libelle: 'IRA haute', count: 38, pct: 34 },
  { code: 'K29', libelle: 'Gastrite', count: 22, pct: 20 },
])

const topExamens = ref([
  { type: 'NFS', count: 98 }, { type: 'Glycémie', count: 76 },
  { type: 'Radiographie', count: 54 }, { type: 'ECBU', count: 43 }, { type: 'ECG', count: 31 },
])

const servicesOccupation = ref([
  { nom: 'Médecine', taux: 85 }, { nom: 'Cardiologie', taux: 60 },
  { nom: 'Maternité', taux: 92 }, { nom: 'Chirurgie', taux: 45 }, { nom: 'Pédiatrie', taux: 70 },
])

const alertesStock = ref([])
const chartOccupation = ref({ labels: [], values: [] })

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const days = periode.value === 'semaine' ? 7 : periode.value === 'mois' ? 30 : periode.value === 'trimestre' ? 90 : 365
    const [summary, labo, finances, alertes, chart] = await Promise.allSettled([
      dashboardService.summary(),
      dashboardService.kpiLabo(days),
      dashboardService.kpiFinances(days),
      pharmacieService.alertes(),
      dashboardService.chartOccupation(7),
    ])
    if (summary.status === 'fulfilled') {
      const d = summary.value.data
      kpis.value[1].value = d.hospitalisations_actives
      kpis.value[2].value = d.examens_en_attente + (labo.status === 'fulfilled' ? labo.value.data.valides : 0)
      kpis.value[3].value = `${((d.chiffre_affaires_mois || 0)/1000000).toFixed(2)} M GNF`
    }
    if (labo.status === 'fulfilled') kpis.value[2].value = labo.value.data.examens_total
    if (alertes.status === 'fulfilled') alertesStock.value = alertes.value.data?.slice(0, 5) || []
    if (chart.status === 'fulfilled') chartOccupation.value = chart.value.data
  } catch { /* mode démo */ }
  finally { loading.value = false }
}

function fmt(n) { return typeof n === 'number' ? n.toLocaleString('fr-FR') : n }
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="page-title">Rapports & Statistiques</h2>
        <p class="text-sm text-gray-500 mt-0.5">Analyse de l'activité hospitalière</p>
      </div>
      <div class="flex gap-2">
        <button v-for="p in ['semaine', 'mois', 'trimestre', 'année']" :key="p"
          @click="periode = p; loadData()"
          :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize', periode === p ? 'bg-violet-600 text-white' : 'bg-white border border-violet-200 text-violet-700']">
          {{ p }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-4 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <!-- KPIs -->
      <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <div v-for="k in kpis" :key="k.label" class="stat-card p-5 card-hover">
          <div class="flex items-start justify-between mb-3">
            <div :class="['kpi-icon', k.color]">{{ k.icon }}</div>
            <span class="text-xs text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded-full">{{ k.variation }}</span>
          </div>
          <p class="text-xl font-bold text-gray-900">{{ fmt(k.value) }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ k.label }}</p>
        </div>
      </div>

      <!-- Alertes stock -->
      <div v-if="alertesStock.length" class="alert-warning-banner">
        <p class="text-sm font-bold text-amber-800 mb-2">⚠ Alertes stock ({{ alertesStock.length }})</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="a in alertesStock" :key="a.id" :class="['text-xs font-medium px-3 py-1 rounded-full', a.statut === 'Rupture' ? 'badge-danger' : 'badge-warning']">
            {{ a.medicament }} — {{ a.quantite }} unités
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <!-- Top diagnostics -->
        <div class="stat-card p-5">
          <p class="section-title mb-4">Top diagnostics (CIM-10)</p>
          <div class="space-y-3">
            <div v-for="d in topDiagnostics" :key="d.code" class="flex items-center gap-3">
              <span class="text-xs font-mono text-violet-600 w-10 shrink-0">{{ d.code }}</span>
              <div class="flex-1">
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-gray-700 font-medium">{{ d.libelle }}</span>
                  <span class="text-gray-500">{{ d.count }} cas</span>
                </div>
                <div class="w-full bg-violet-100 rounded-full h-2">
                  <div class="bg-violet-600 h-2 rounded-full transition-all" :style="{ width: d.pct + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top examens -->
        <div class="stat-card p-5">
          <p class="section-title mb-4">Examens les plus prescrits</p>
          <div class="space-y-3">
            <div v-for="(e, i) in topExamens" :key="e.type" class="flex items-center gap-3">
              <div class="w-7 h-7 rounded-lg bg-violet-100 flex items-center justify-center text-violet-700 font-bold text-xs shrink-0">{{ i + 1 }}</div>
              <div class="flex-1">
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-gray-700 font-medium">{{ e.type }}</span>
                  <span class="text-gray-500">{{ e.count }}</span>
                </div>
                <div class="w-full bg-blue-100 rounded-full h-2">
                  <div class="bg-blue-500 h-2 rounded-full" :style="{ width: Math.round((e.count / 98) * 100) + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Taux occupation + courbe -->
      <div class="stat-card p-5">
        <p class="section-title mb-4">Taux d'occupation par service</p>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <div v-for="s in servicesOccupation" :key="s.nom" class="text-center">
            <div class="relative w-16 h-16 mx-auto mb-2">
              <svg class="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#ede9fe" stroke-width="3"/>
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#7c3aed" stroke-width="3"
                  :stroke-dasharray="`${s.taux} ${100 - s.taux}`" stroke-linecap="round"/>
              </svg>
              <span class="absolute inset-0 flex items-center justify-center text-xs font-bold text-violet-700">{{ s.taux }}%</span>
            </div>
            <p class="text-xs text-gray-600 font-medium">{{ s.nom }}</p>
          </div>
        </div>
      </div>

      <!-- Courbe occupation 7j -->
      <div v-if="chartOccupation.labels?.length" class="stat-card p-5">
        <p class="section-title mb-4">Évolution taux d'occupation (7 jours)</p>
        <div class="flex items-end gap-2 h-32">
          <div v-for="(v, i) in chartOccupation.values" :key="i" class="flex-1 flex flex-col items-center gap-1">
            <span class="text-xs text-gray-500">{{ v }}%</span>
            <div class="w-full rounded-t-md transition-all" :style="{ height: v + '%', background: v > 85 ? '#ef4444' : v > 70 ? '#f59e0b' : '#7c3aed' }"></div>
            <span class="text-[10px] text-gray-400">{{ chartOccupation.labels[i]?.slice(5) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
