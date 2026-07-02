"""
WebSocket Consumers pour chat temps réel
"""
import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer pour conversations médecin-patient
    """
    
    async def connect(self):
        """Établissement connexion WebSocket"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Auth user
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return
        
        # Rejoindre le groupe de la conversation
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"User {user.id} connecté à la conversation {self.conversation_id}")
        
        # Envoyer message de bienvenue
        await self.send(json.dumps({
            'type': 'connection_established',
            'message': 'Connecté au chat',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Déconnexion WebSocket"""
        # Quitter le groupe
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
    
    async def receive(self, text_data):
        """Réception message WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            else:
                logger.warning(f"Type de message inconnu: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON invalide: {e}")
            await self.send_error("Message invalide")
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            await self.send_error("Erreur serveur")
    
    async def handle_message(self, data):
        """Gérer un nouveau message"""
        message = data.get('content', '')
        
        if not message:
            await self.send_error("Contenu vide")
            return
        
        user = self.scope['user']
        
        # Sauvegarder le message dans la base
        message_id = await self.save_message(
            conversation_id=self.conversation_id,
            user=user,
            content=message
        )
        
        # Envoyer au groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message_id,
                'content': message,
                'sender_id': user.id,
                'sender_name': f"{user.nom} {user.prenom}",
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_read_receipt(self, data):
        """Gérer accusé de lecture"""
        message_id = data.get('message_id')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'user_id': self.scope['user'].id,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_typing(self, data):
        """Gérer indicateur de frappe"""
        is_typing = data.get('typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.scope['user'].id,
                'user_name': f"{self.scope['user'].nom} {self.scope['user'].prenom}",
                'typing': is_typing
            }
        )
    
    async def chat_message(self, event):
        """Envoyer message aux clients"""
        await self.send(json.dumps({
            'type': 'new_message',
            'message_id': event['message_id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))
    
    async def read_receipt(self, event):
        """Envoyer accusé de lecture"""
        await self.send(json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))
    
    async def typing_indicator(self, event):
        """Envoyer indicateur de frappe"""
        await self.send(json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'typing': event['typing']
        }))
    
    async def send_error(self, error_message):
        """Envoyer message d'erreur"""
        await self.send(json.dumps({
            'type': 'error',
            'message': error_message
        }))
    
    @database_sync_to_async
    def save_message(self, conversation_id, user, content):
        """Sauvegarder message dans la base (sync)"""
        from .models import Message, Conversation
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Vérifier autorisation
            if user not in [conversation.patient, conversation.medecin]:
                raise PermissionError("Accès non autorisé")
            
            message = Message.objects.create(
                conversation=conversation,
                sender=user,
                content=content
            )
            
            return message.id
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde message: {e}")
            raise


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer pour notifications push
    """
    
    async def connect(self):
        """Établissement connexion notifications"""
        user = self.scope.get('user')
        
        if not user or not user.is_authenticated:
            await self.close()
            return
        
        self.user_id = user.id
        self.room_group_name = f'notifications_{self.user_id}'
        
        # Rejoindre le groupe de notifications
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"User {self.user_id} connecté aux notifications")
    
    async def disconnect(self, close_code):
        """Déconnexion notifications"""
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Erreur déconnexion notifications: {e}")
    
    async def send_notification(self, event):
        """Envoyer notification"""
        await self.send(json.dumps({
            'type': 'notification',
            'title': event['title'],
            'body': event['body'],
            'data': event.get('data', {}),
            'timestamp': event['timestamp']
        }))
    
    @classmethod
    async def send_to_user(cls, user_id: int, title: str, body: str, data: dict = None):
        """Méthode de classe pour envoyer notification à un utilisateur"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        room_group_name = f'notifications_{user_id}'
        
        await channel_layer.group_send(
            room_group_name,
            {
                'type': 'send_notification',
                'title': title,
                'body': body,
                'data': data or {},
                'timestamp': timezone.now().isoformat()
            }
        )
