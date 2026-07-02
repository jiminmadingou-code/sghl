import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'

const app   = createApp(App)
const pinia = createPinia()

// Handler global d'erreurs Vue — empêche les pages blanches silencieuses
app.config.errorHandler = (err, instance, info) => {
  console.error('[SGHL] Erreur composant:', err, info)
}
app.config.warnHandler = (msg) => {
  // Silencer les warnings non critiques en prod
  if (import.meta.env.DEV) console.warn('[SGHL]', msg)
}

// Pinia AVANT router — ordre critique
app.use(pinia)
app.use(router)
app.mount('#app')
