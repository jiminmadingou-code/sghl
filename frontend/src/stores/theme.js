import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // Charger le thème depuis localStorage ou préférence système
  const preferred = localStorage.getItem('sghl_theme')
  const isDark = ref(preferred === 'dark' || (!preferred && window.matchMedia('(prefers-color-scheme: dark)').matches))

  // Appliquer le thème sur <html>
  function applyTheme() {
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
    localStorage.setItem('sghl_theme', isDark.value ? 'dark' : 'light')
  }

  // Appliquer au montage
  applyTheme()

  // Basculer le thème
  function toggle() {
    isDark.value = !isDark.value
    applyTheme()
  }

  // Watcher pour s'adapter aux changements système
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('sghl_theme')) {
      isDark.value = e.matches
      applyTheme()
    }
  })

  return { isDark, toggle }
})
