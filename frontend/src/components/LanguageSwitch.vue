<script setup>
import { useI18nStore } from '@/stores/i18n'

const i18n = useI18nStore()
</script>

<template>
  <div class="relative">
    <button @click="i18n.toggleLang()"
      class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 border border-white/20 text-white/80 hover:bg-white/20 hover:text-white transition-all text-xs font-semibold">
      <span class="text-sm">{{ i18n.currentLang === 'fr' ? '🇫🇷' : '🇬🇧' }}</span>
      <span class="hidden sm:inline">{{ i18n.currentLang === 'fr' ? 'FR' : 'EN' }}</span>
    </button>
  </div>
</template>
