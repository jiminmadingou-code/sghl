<script setup>
import { ref } from 'vue'

const activeSection = ref('general')

const sections = [
  { key: 'general', label: 'Général', icon: '🏥' },
  { key: 'securite', label: 'Sécurité', icon: '🔒' },
  { key: 'notifications', label: 'Notifications', icon: '🔔' },
  { key: 'sauvegarde', label: 'Sauvegarde', icon: '💾' },
]

const config = ref({
  nom_hopital: 'Hôpital Central de Conakry',
  adresse: 'Conakry, Guinée',
  telephone: '+224 620 000 000',
  email: 'contact@hopital.gn',
  mfa_enabled: true,
  session_timeout: 30,
  password_expiry: 90,
  notif_email: true,
  notif_push: true,
  notif_sms: false,
  backup_auto: true,
  backup_freq: 'Quotidien',
})
</script>

<template>
  <div class="space-y-5">
    <div>
      <h2 class="page-title">Paramètres système</h2>
      <p class="text-sm text-gray-500 mt-0.5">Configuration de la plateforme SGHL</p>
    </div>

    <div class="flex gap-5">
      <!-- Sidebar sections -->
      <div class="w-48 shrink-0 space-y-1">
        <button
          v-for="s in sections" :key="s.key"
          @click="activeSection = s.key"
          :class="['w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-left',
            activeSection === s.key ? 'bg-violet-600 text-white' : 'text-gray-600 hover:bg-violet-50']"
        >
          <span>{{ s.icon }}</span> {{ s.label }}
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 stat-card p-6">

        <!-- Général -->
        <div v-if="activeSection === 'general'" class="space-y-4">
          <p class="section-title">Informations de l'établissement</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Nom de l'hôpital</label>
              <input v-model="config.nom_hopital" class="input-field" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Email</label>
              <input v-model="config.email" type="email" class="input-field" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Téléphone</label>
              <input v-model="config.telephone" class="input-field" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Adresse</label>
              <input v-model="config.adresse" class="input-field" />
            </div>
          </div>
          <button class="btn-primary mt-2">Enregistrer</button>
        </div>

        <!-- Sécurité -->
        <div v-if="activeSection === 'securite'" class="space-y-5">
          <p class="section-title">Politique de sécurité</p>
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-violet-50 rounded-xl">
              <div>
                <p class="text-sm font-medium text-gray-900">Authentification MFA</p>
                <p class="text-xs text-gray-500">Double facteur obligatoire pour tous les comptes</p>
              </div>
              <button
                @click="config.mfa_enabled = !config.mfa_enabled"
                :class="['w-12 h-6 rounded-full transition-colors relative', config.mfa_enabled ? 'bg-violet-600' : 'bg-gray-300']"
              >
                <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform', config.mfa_enabled ? 'translate-x-6' : 'translate-x-0.5']"></span>
              </button>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Timeout session (min)</label>
                <input v-model="config.session_timeout" type="number" class="input-field" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Expiration mot de passe (jours)</label>
                <input v-model="config.password_expiry" type="number" class="input-field" />
              </div>
            </div>
          </div>
          <button class="btn-primary">Enregistrer</button>
        </div>

        <!-- Notifications -->
        <div v-if="activeSection === 'notifications'" class="space-y-4">
          <p class="section-title">Canaux de notification</p>
          <div v-for="(label, key) in { notif_email: 'Notifications Email', notif_push: 'Notifications Push', notif_sms: 'Notifications SMS' }" :key="key"
               class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <p class="text-sm font-medium text-gray-900">{{ label }}</p>
            <button
              @click="config[key] = !config[key]"
              :class="['w-12 h-6 rounded-full transition-colors relative', config[key] ? 'bg-violet-600' : 'bg-gray-300']"
            >
              <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform', config[key] ? 'translate-x-6' : 'translate-x-0.5']"></span>
            </button>
          </div>
          <button class="btn-primary">Enregistrer</button>
        </div>

        <!-- Sauvegarde -->
        <div v-if="activeSection === 'sauvegarde'" class="space-y-4">
          <p class="section-title">Politique de sauvegarde</p>
          <div class="flex items-center justify-between p-4 bg-green-50 rounded-xl">
            <div>
              <p class="text-sm font-medium text-gray-900">Sauvegarde automatique</p>
              <p class="text-xs text-gray-500">Dernière sauvegarde : aujourd'hui à 03:00</p>
            </div>
            <button
              @click="config.backup_auto = !config.backup_auto"
              :class="['w-12 h-6 rounded-full transition-colors relative', config.backup_auto ? 'bg-green-500' : 'bg-gray-300']"
            >
              <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform', config.backup_auto ? 'translate-x-6' : 'translate-x-0.5']"></span>
            </button>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Fréquence</label>
            <select v-model="config.backup_freq" class="input-field max-w-xs">
              <option>Quotidien</option>
              <option>Hebdomadaire</option>
              <option>Mensuel</option>
            </select>
          </div>
          <button class="btn-primary">Lancer une sauvegarde maintenant</button>
        </div>
      </div>
    </div>
  </div>
</template>
