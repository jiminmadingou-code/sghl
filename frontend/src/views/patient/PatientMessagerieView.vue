<script setup>
import { ref, computed, nextTick } from 'vue'

const activeConv = ref(1)
const newMessage = ref('')
const messagesEnd = ref(null)

const conversations = ref([
  { id: 1, interlocuteur: 'Dr. Camara Alpha', role: 'Médecin référent', service: 'Médecine interne', avatar: 'CA', nonLus: 1, dernierMsg: 'Vos résultats sont bons dans l\'ensemble...', heure: '11:32' },
  { id: 2, interlocuteur: 'Secrétariat médical', role: 'Administration', service: 'DIGNE HOSPITAL', avatar: 'SM', nonLus: 0, dernierMsg: 'Votre RDV du 18 juin est confirmé.', heure: 'Hier' },
  { id: 3, interlocuteur: 'Dr. Bah Mariama', role: 'Cardiologue', service: 'Cardiologie', avatar: 'BM', nonLus: 0, dernierMsg: 'N\'oubliez pas de prendre votre traitement...', heure: 'Lun' },
])

const messages = ref({
  1: [
    { id: 1, de: 'Dr. Camara Alpha', moi: false, texte: 'Bonjour M. Diallo, j\'ai bien reçu vos résultats d\'examens.', heure: '11:20', date: 'Aujourd\'hui' },
    { id: 2, de: 'Moi', moi: true,  texte: 'Bonjour Docteur, merci. Est-ce que tout est normal ?', heure: '11:25', date: 'Aujourd\'hui' },
    { id: 3, de: 'Dr. Camara Alpha', moi: false, texte: 'Vos résultats sont bons dans l\'ensemble. L\'hémoglobine est légèrement basse, je vous recommande de prendre du fer pendant 1 mois. La glycémie est un peu élevée, continuez le régime alimentaire.', heure: '11:32', date: 'Aujourd\'hui' },
  ],
  2: [
    { id: 1, de: 'Secrétariat médical', moi: false, texte: 'Bonjour, votre rendez-vous du 18 juin à 09h30 avec Dr. Camara est confirmé. Merci de vous présenter 15 minutes avant.', heure: '14:00', date: 'Hier' },
    { id: 2, de: 'Moi', moi: true, texte: 'Merci pour la confirmation.', heure: '14:15', date: 'Hier' },
  ],
  3: [
    { id: 1, de: 'Dr. Bah Mariama', moi: false, texte: 'N\'oubliez pas de prendre votre Amlodipine chaque matin. À bientôt pour votre ECG de contrôle.', heure: '09:00', date: 'Lundi' },
  ],
})

const currentConv = computed(() => conversations.value.find(c => c.id === activeConv.value))
const currentMessages = computed(() => messages.value[activeConv.value] || [])

async function sendMessage() {
  if (!newMessage.value.trim()) return
  const msgs = messages.value[activeConv.value]
  msgs.push({ id: Date.now(), de: 'Moi', moi: true, texte: newMessage.value.trim(), heure: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }), date: 'Aujourd\'hui' })
  newMessage.value = ''
  await nextTick()
  messagesEnd.value?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div class="space-y-4">
    <div>
      <h1 class="text-2xl font-extrabold text-gray-900">Messagerie sécurisée</h1>
      <p class="text-sm text-gray-500 mt-0.5">Échangez en toute confidentialité avec votre équipe médicale</p>
    </div>

    <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden" style="height: 600px; display: flex;">

      <!-- Liste conversations -->
      <div class="w-72 shrink-0 border-r border-gray-100 flex flex-col">
        <div class="p-4 border-b border-gray-100">
          <input class="input-field text-xs" placeholder="🔍 Rechercher..." />
        </div>
        <div class="flex-1 overflow-y-auto">
          <button v-for="conv in conversations" :key="conv.id"
            @click="activeConv = conv.id"
            :class="['w-full flex items-start gap-3 p-4 border-b border-gray-50 hover:bg-blue-50/50 transition-colors text-left',
              activeConv === conv.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : '']">
            <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0">
              {{ conv.avatar }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <p class="font-semibold text-gray-900 text-sm truncate">{{ conv.interlocuteur }}</p>
                <span class="text-[10px] text-gray-400 shrink-0 ml-1">{{ conv.heure }}</span>
              </div>
              <p class="text-xs text-gray-500 truncate">{{ conv.role }}</p>
              <p class="text-xs text-gray-400 truncate mt-0.5">{{ conv.dernierMsg }}</p>
            </div>
            <span v-if="conv.nonLus" class="w-5 h-5 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-1">
              {{ conv.nonLus }}
            </span>
          </button>
        </div>
      </div>

      <!-- Zone conversation -->
      <div class="flex-1 flex flex-col min-w-0">

        <!-- Header conv -->
        <div v-if="currentConv" class="flex items-center gap-3 px-5 py-4 border-b border-gray-100 bg-gray-50 shrink-0">
          <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shrink-0">
            {{ currentConv.avatar }}
          </div>
          <div>
            <p class="font-bold text-gray-900 text-sm">{{ currentConv.interlocuteur }}</p>
            <p class="text-xs text-gray-500">{{ currentConv.role }} · {{ currentConv.service }}</p>
          </div>
          <div class="ml-auto flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-green-400"></span>
            <span class="text-xs text-gray-400">En ligne</span>
          </div>
        </div>

        <!-- Messages -->
        <div class="flex-1 overflow-y-auto p-5 space-y-4">
          <template v-for="(msg, i) in currentMessages" :key="msg.id">
            <div v-if="i === 0 || currentMessages[i-1].date !== msg.date" class="text-center">
              <span class="text-[10px] bg-gray-100 text-gray-500 px-3 py-1 rounded-full font-medium">{{ msg.date }}</span>
            </div>
            <div :class="['flex', msg.moi ? 'justify-end' : 'justify-start']">
              <div :class="['max-w-xs lg:max-w-md', msg.moi ? 'items-end' : 'items-start', 'flex flex-col gap-1']">
                <div :class="['px-4 py-2.5 rounded-2xl text-sm leading-relaxed',
                  msg.moi
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-gray-100 text-gray-900 rounded-bl-sm']">
                  {{ msg.texte }}
                </div>
                <span class="text-[10px] text-gray-400 px-1">{{ msg.heure }}</span>
              </div>
            </div>
          </template>
          <div ref="messagesEnd"></div>
        </div>

        <!-- Input message -->
        <div class="px-4 py-3 border-t border-gray-100 bg-white shrink-0">
          <div class="flex items-center gap-2">
            <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors shrink-0">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
              </svg>
            </button>
            <input v-model="newMessage" @keyup.enter="sendMessage"
              class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all"
              placeholder="Écrivez votre message..." />
            <button @click="sendMessage"
              :disabled="!newMessage.trim()"
              class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white hover:bg-blue-700 transition-colors disabled:opacity-40 shrink-0">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </button>
          </div>
          <p class="text-[10px] text-gray-400 mt-1.5 px-1">🔒 Messages chiffrés de bout en bout · Réponse sous 24h ouvrées</p>
        </div>
      </div>
    </div>
  </div>
</template>
