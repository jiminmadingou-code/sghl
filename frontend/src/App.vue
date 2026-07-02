<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useToastStore } from '@/stores/toast'
const toast = useToastStore()

function onLoginNotif(e) {
  const { email, telephone, name } = e.detail
  toast.add(`📧 Notification de connexion envoyée à ${email}`, 'info', 5000)
  if (telephone) toast.add(`📱 SMS de sécurité envoyé au ${telephone}`, 'info', 5000)
}

onMounted(() => window.addEventListener('sghl:login-notif', onLoginNotif))
onUnmounted(() => window.removeEventListener('sghl:login-notif', onLoginNotif))
</script>

<template>
  <RouterView />

  <!-- Toast global -->
  <Teleport to="body">
    <div class="fixed bottom-6 right-6 z-[200] flex flex-col gap-2 pointer-events-none">
      <transition-group name="toast">
        <div v-for="t in toast.toasts" :key="t.id"
          :class="['flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl text-sm font-semibold pointer-events-auto',
            t.type === 'success' ? 'bg-green-600 text-white' :
            t.type === 'error'   ? 'bg-red-600 text-white' :
            t.type === 'warning' ? 'bg-amber-500 text-white' :
            'bg-gray-900 text-white']">
          <span class="text-base">
            {{ t.type === 'success' ? '✅' : t.type === 'error' ? '❌' : t.type === 'warning' ? '⚠️' : 'ℹ️' }}
          </span>
          <span>{{ t.message }}</span>
          <button @click="toast.remove(t.id)" class="ml-2 opacity-70 hover:opacity-100 text-lg leading-none">×</button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<style>
.toast-enter-active { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(50px) scale(0.95); }
.toast-leave-to     { opacity: 0; transform: translateX(50px); }
</style>
