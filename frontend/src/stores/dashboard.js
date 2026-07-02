import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardService } from '@/services/sghl'

export const useDashboardStore = defineStore('dashboard', () => {
  const summary   = ref(null)
  const loading   = ref(false)
  const lastFetch = ref(null)
  const CACHE_MS  = 5 * 60 * 1000 // 5 min

  async function fetchSummary(force = false) {
    if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_MS) return
    loading.value = true
    try {
      const { data } = await dashboardService.summary()
      summary.value  = data
      lastFetch.value = Date.now()
    } catch (e) {
      console.warn('Dashboard API indisponible, mode démo actif')
    } finally {
      loading.value = false
    }
  }

  return { summary, loading, fetchSummary }
})
