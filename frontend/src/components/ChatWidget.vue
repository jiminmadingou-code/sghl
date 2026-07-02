<template>
  <div class="chat-widget" :class="{ 'open': isOpen }">
    <!-- Bouton d'ouverture -->
    <button @click="toggleChat" class="chat-toggle" v-if="!isOpen">
      <i class="icon-message"></i>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>

    <!-- Fenêtre de chat -->
    <div class="chat-window">
      <div class="chat-header">
        <h3>Messagerie</h3>
        <div class="header-actions">
          <button @click="newConversation" class="btn-new">
            <i class="icon-plus"></i>
          </button>
          <button @click="toggleChat" class="btn-close">
            <i class="icon-close"></i>
          </button>
        </div>
      </div>

      <!-- Liste des conversations -->
      <div class="conversations-list" v-if="!selectedConversation">
        <div class="search-box">
          <input v-model="searchQuery" placeholder="Rechercher..." />
        </div>
        <div class="conversations">
          <div
            v-for="conv in filteredConversations"
            :key="conv.id"
            @click="selectConversation(conv)"
            class="conversation-item"
            :class="{ active: conv.id === selectedConversation?.id }"
          >
            <div class="avatar">{{ getInitials(conv.patient_nom) }}</div>
            <div class="info">
              <div class="name">{{ conv.patient_nom }}</div>
              <div class="last-message">{{ conv.dernier_message }}</div>
            </div>
            <div class="meta">
              <span class="time">{{ formatTime(conv.date_dernier_message) }}</span>
              <span v-if="conv.message_non_lus > 0" class="unread-badge">{{ conv.message_non_lus }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Zone de message -->
      <div class="chat-area" v-else>
        <div class="chat-messages">
          <div class="messages-header">
            <button @click="backToConversations" class="btn-back">
              <i class="icon-arrow-left"></i>
            </button>
            <h4>{{ selectedConversation.patient_nom }}</h4>
          </div>
          
          <div class="messages-list" ref="messagesContainer">
            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message"
              :class="{ 'own': msg.own }"
            >
              <div class="bubble">
                {{ msg.contenu }}
              </div>
              <div class="meta">
                {{ formatMessageTime(msg.date_envoi) }}
                <span v-if="msg.lu" class="read-indicator">✓✓</span>
              </div>
            </div>
            
            <!-- Loading indicator -->
            <div v-if="loading" class="message loading">
              <div class="bubble">...</div>
            </div>
          </div>
        </div>

        <div class="message-input">
          <textarea
            v-model="newMessage"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="Tapez votre message..."
            rows="1"
          ></textarea>
          <button @click="sendMessage" :disabled="!newMessage.trim()">
            <i class="icon-send"></i>
          </button>
        </div>
      </div>

      <!-- Notifications -->
      <div class="notifications-panel" v-if="showNotifications">
        <div class="panel-header">
          <h4>Notifications</h4>
          <button @click="showNotifications = false">Fermer</button>
        </div>
        <div class="notifications-list">
          <div
            v-for="notif in notifications"
            :key="notif.id"
            class="notification-item"
            :class="{ read: notif.lu }"
            @click="markNotificationRead(notif)"
          >
            <div class="notif-title">{{ notif.titre }}</div>
            <div class="notif-message">{{ notif.message }}</div>
            <div class="notif-time">{{ formatTime(notif.date_creation) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';

export default {
  name: 'ChatWidget',
  setup() {
    const authStore = useAuthStore();
    const isOpen = ref(false);
    const showNotifications = ref(false);
    const conversations = ref([]);
    const selectedConversation = ref(null);
    const messages = ref([]);
    const newMessage = ref('');
    const loading = ref(false);
    const searchQuery = ref('');
    const unreadCount = ref(0);
    const notifications = ref([]);
    const messagesContainer = ref(null);

    // Charger les conversations
    const loadConversations = async () => {
      try {
        const response = await api.get('/chat/conversations/');
        conversations.value = response.data;
        updateUnreadCount();
      } catch (error) {
        console.error('Erreur chargement conversations:', error);
      }
    };

    // Charger les messages
    const loadMessages = async (conversationId) => {
      loading.value = true;
      try {
        const response = await api.get(`/chat/conversations/${conversationId}/messages/`);
        messages.value = response.data.map(msg => ({
          ...msg,
          own: msg.expediteur_id === authStore.user?.id
        }));
        await nextTick();
        scrollToBottom();
      } catch (error) {
        console.error('Erreur chargement messages:', error);
      } finally {
        loading.value = false;
      }
    };

    // Envoyer un message
    const sendMessage = async () => {
      if (!newMessage.value.trim() || !selectedConversation.value) return;

      const content = newMessage.value;
      newMessage.value = '';

      try {
        await api.post('/chat/messages/', {
          conversation_id: selectedConversation.value.id,
          contenu: content
        });

        // Ajouter localement
        messages.value.push({
          id: Date.now(),
          contenu: content,
          own: true,
          lu: false,
          date_envoi: new Date().toISOString()
        });

        await nextTick();
        scrollToBottom();
        loadConversations(); // Rafraîchir la liste
      } catch (error) {
        console.error('Erreur envoi message:', error);
        newMessage.value = content; // Restaurer
      }
    };

    // Charger les notifications
    const loadNotifications = async () => {
      try {
        const response = await api.get('/chat/notifications/?unread_only=true');
        notifications.value = response.data;
      } catch (error) {
        console.error('Erreur chargement notifications:', error);
      }
    };

    // Marquer notification comme lue
    const markNotificationRead = async (notif) => {
      if (notif.lu) return;
      
      try {
        await api.put(`/chat/notifications/${notif.id}/read`);
        notif.lu = true;
        updateUnreadCount();
      } catch (error) {
        console.error('Erreur mark read:', error);
      }
    };

    // Compteur non lus
    const updateUnreadCount = () => {
      unreadCount.value = conversations.value.reduce((acc, conv) => 
        acc + (conv.message_non_lus || 0), 0
      );
    };

    // Filtrer conversations
    const filteredConversations = computed(() => {
      if (!searchQuery.value) return conversations.value;
      return conversations.value.filter(conv =>
        conv.patient_nom?.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    // Helpers
    const toggleChat = () => {
      isOpen.value = !isOpen.value;
      if (isOpen.value) {
        loadConversations();
        loadNotifications();
      }
    };

    const selectConversation = (conv) => {
      selectedConversation.value = conv;
      loadMessages(conv.id);
    };

    const backToConversations = () => {
      selectedConversation.value = null;
      messages.value = [];
    };

    const newConversation = () => {
      // TODO: Ouvrir modal sélection patient
      console.log('Nouvelle conversation');
    };

    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };

    const formatTime = (dateStr) => {
      const date = new Date(dateStr);
      return date.toLocaleDateString('fr-FR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const formatMessageTime = (dateStr) => {
      const date = new Date(dateStr);
      return date.toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const getInitials = (name) => {
      return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '?';
    };

    // Polling pour nouvelles messages (remplacement WebSocket)
    let pollingInterval;
    const startPolling = () => {
      pollingInterval = setInterval(() => {
        if (selectedConversation.value) {
          loadMessages(selectedConversation.value.id);
        }
        loadConversations();
      }, 5000); // 5 secondes
    };

    const stopPolling = () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };

    onMounted(() => {
      loadConversations();
      startPolling();
    });

    watch(isOpen, (open) => {
      if (!open) {
        stopPolling();
      } else {
        startPolling();
      }
    });

    return {
      isOpen,
      showNotifications,
      conversations,
      selectedConversation,
      messages,
      newMessage,
      loading,
      searchQuery,
      unreadCount,
      notifications,
      filteredConversations,
      messagesContainer,
      toggleChat,
      selectConversation,
      backToConversations,
      newConversation,
      sendMessage,
      markNotificationRead,
      formatTime,
      formatMessageTime,
      getInitials
    };
  }
};
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.chat-toggle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #2563eb;
  color: white;
  border: none;
  cursor: pointer;
  position: relative;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.chat-window {
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px;
  background: #2563eb;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-new, .btn-close {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
}

.search-box {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.conversation-item {
  display: flex;
  padding: 12px;
  gap: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
}

.conversation-item:hover {
  background: #f9fafb;
}

.conversation-item.active {
  background: #eff6ff;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #dbeafe;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.info {
  flex: 1;
  overflow: hidden;
}

.name {
  font-weight: 600;
  margin-bottom: 4px;
}

.last-message {
  color: #6b7280;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.time {
  font-size: 12px;
  color: #9ca3af;
}

.unread-badge {
  background: #2563eb;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}

.chat-area {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
}

.messages-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.messages-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message.own {
  align-items: flex-end;
}

.bubble {
  padding: 10px 14px;
  border-radius: 12px;
  background: #f3f4f6;
  word-wrap: break-word;
}

.message.own .bubble {
  background: #2563eb;
  color: white;
}

.message .meta {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 4px;
  display: flex;
  gap: 4px;
  align-items: center;
}

.read-indicator {
  color: #2563eb;
}

.message-input {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
}

.message-input textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
}

.message-input button {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.message-input button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.notifications-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background: white;
  z-index: 10;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notifications-list {
  padding: 12px;
  overflow-y: auto;
  height: calc(100% - 60px);
}

.notification-item {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin-bottom: 8px;
  cursor: pointer;
}

.notification-item:hover {
  background: #f9fafb;
}

.notification-item.read {
  opacity: 0.6;
}

.notif-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.notif-message {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.notif-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>
