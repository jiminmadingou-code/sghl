from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import datetime
from django.utils import timezone
from .models import Conversation, Message, NotificationPush, DeviceToken

router = Router(tags=['Chat & Notifications'])


class ConversationOut(Schema):
    id: int
    patient_id: int
    medicecin_id: int
    sujet: str
    date_creation: datetime
    date_dernier_message: datetime
    dernier_message: Optional[str] = None
    message_non_lus: int = 0


class MessageIn(Schema):
    conversation_id: int
    contenu: str
    piece_jointe: Optional[str] = None


class MessageOut(Schema):
    id: int
    conversation_id: int
    expediteur_id: int
    contenu: str
    date_envoi: datetime
    lu: bool
    piece_jointe: Optional[str] = None


class NotificationOut(Schema):
    id: int
    titre: str
    message: str
    type_notification: str
    lue: bool
    date_creation: datetime


@router.get('/conversations/', response=List[ConversationOut])
def list_conversations(request, medecin_id: Optional[int] = None):
    """Lister les conversations de l'utilisateur."""
    if medecin_id:
        qs = Conversation.objects.filter(medicecin_id=medecin_id)
    else:
        # TODO: Récupérer depuis request.user
        qs = Conversation.objects.all()
    
    conversations = []
    for conv in qs[:50]:
        dernier_msg = conv.messages.last()
        non_lus = conv.messages.filter(
            lu=False,
            expediteur__isnull=False
        ).count()
        
        conversations.append(ConversationOut(
            id=conv.id,
            patient_id=conv.patient_id,
            medicecin_id=conv.medicecin_id,
            sujet=conv.sujet,
            date_creation=conv.date_creation,
            date_dernier_message=conv.date_dernier_message,
            dernier_message=dernier_msg.contenu[:100] if dernier_msg else '',
            message_non_lus=non_lus,
        ))
    
    return conversations


@router.get('/conversations/{conversation_id}/messages', response=List[MessageOut])
def list_messages(request, conversation_id: int, limit: int = 50):
    """Lister les messages d'une conversation."""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    messages = conv.messages.all().order_by('-date_envoi')[:limit]
    return list(reversed(messages))


@router.post('/conversations/', response=ConversationOut)
def create_conversation(request, patient_id: int, medecin_id: int, sujet: str = ''):
    """Créer une nouvelle conversation."""
    conv, created = Conversation.objects.get_or_create(
        patient_id=patient_id,
        medicecin_id=medecin_id,
        defaults={'sujet': sujet}
    )
    return conv


@router.post('/messages/', response=MessageOut)
def send_message(request, payload: MessageIn):
    """Envoyer un message."""
    conv = get_object_or_404(Conversation, id=payload.conversation_id)
    
    # TODO: Récupérer expediteur depuis request.user
    message = Message.objects.create(
        conversation=conv,
        contenu=payload.contenu,
        # expediteur=...
    )
    
    # Envoyer notification push
    NotificationPush.objects.create(
        utilisateur_id=conv.patient_id,  # ou medecin selon destinataire
        type_notification='message',
        titre='Nouveau message',
        message=payload.contenu[:200],
        data_contexte={'conversation_id': conv.id}
    )
    
    return message


@router.put('/messages/{message_id}/read')
def mark_message_read(request, message_id: int):
    """Marquer un message comme lu."""
    msg = get_object_or_404(Message, id=message_id)
    msg.marquer_comme_lue()
    return {'success': True}


@router.get('/notifications/', response=List[NotificationOut])
def list_notifications(request, unread_only: bool = False):
    """Lister les notifications."""
    qs = NotificationPush.objects.all()
    if unread_only:
        qs = qs.filter(lue=False)
    return qs[:100]


@router.put('/notifications/{notif_id}/read')
def mark_notification_read(request, notif_id: int):
    """Marquer une notification comme lue."""
    notif = get_object_or_404(NotificationPush, id=notif_id)
    notif.marquer_comme_lue()
    return {'success': True}


@router.post('/notifications/register-device')
def register_device(request, token: str, device_type: str, nom_appareil: str = ''):
    """Enregistrer un appareil pour notifications push."""
    # TODO: Récupérer utilisateur depuis request.user
    device, created = DeviceToken.objects.get_or_create(
        token=token,
        defaults={
            'device_type': device_type,
            'nom_appareil': nom_appareil,
        }
    )
    return {'success': True, 'created': created}


@router.get('/unread-count')
def get_unread_count(request):
    """Compter les messages et notifications non lus."""
    # TODO: Récupérer utilisateur depuis request.user
    return {
        'messages_non_lus': Message.objects.filter(lu=False).count(),
        'notifications_non_lues': NotificationPush.objects.filter(lue=False).count(),
    }
