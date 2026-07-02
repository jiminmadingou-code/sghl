import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])

  function add(message, type = 'info', duration = 4000) {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    setTimeout(() => remove(id), duration)
  }

  function remove(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  const success = (msg) => add(msg, 'success')
  const error   = (msg) => add(msg, 'error')
  const warning = (msg) => add(msg, 'warning')
  const info    = (msg) => add(msg, 'info')

  return { toasts, add, remove, success, error, warning, info }
})
