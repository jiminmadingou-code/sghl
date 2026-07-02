"""
Modèles pour le système de chat temps réel médecin-patient
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Conversation(models.Model):
    """Conversation entre médecin et patient."""
    STATUT_CHOICES = [
        ('ouverte', 'Ouverte'),
        ('fermee', 'Fermée'),
        ('archivée', 'Archivée'),
    ]

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    medicecin = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.CASCADE,
        related_name='conversations_medecin'
    )
    sujet = models.CharField(max_length=200, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_dernier_message = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouverte')
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )

    class Meta:
        ordering = ['-date_dernier_message']
        indexes = [
            models.Index(fields=['patient', 'statut']),
            models.Index(fields=['medicecin', 'statut']),
        ]

    def __str__(self):
        return f"{self.patient.nom} - {self.medicecin.nom} ({self.date_creation})"

    def marquer_comme_lue(self, participant):
        """Marquer tous les messages comme lus par le participant."""
        Message.objects.filter(
            conversation=self,
            expediteur__user=participant
        ).update(lu=True)


class Message(models.Model):
    """Message dans une conversation."""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    expediteur = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.PROTECT,
        related_name='messages_envoyes'
    )
    destinataire = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='messages_recus'
    )
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Pièces jointes
    piece_jointe = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    type_piece_jointe = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['date_envoi']
        indexes = [
            models.Index(fields=['conversation', '-date_envoi']),
            models.Index(fields=['lu', 'destinataire']),
        ]

    def __str__(self):
        return f"{self.expediteur.nom}: {self.contenu[:50]}..."

    def marquer_comme_lu(self):
        """Marquer le message comme lu."""
        self.lu = True
        self.date_lecture = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        if self.pk is None and self.destinataire:
            # Premier message - envoyer notification
            from dashboard.models import NotificationSysteme
            NotificationSysteme.objects.create(
                titre='Nouveau message',
                type_notification='alerte_patient',
                description=f"Nouveau message de {self.expediteur.nom}",
                priorite='medium',
                lu=False
            )
        super().save(*args, **kwargs)


class NotificationPush(models.Model):
    """Notifications push pour l'application mobile."""
    TYPE_NOTIFICATION = [
        ('message', 'Nouveau Message'),
        ('rendez_vous', 'Rappel Rendez-vous'),
        ('ordonnance', 'Nouvelle Ordonnance'),
        ('resultat', 'Résultat Disponible'),
        ('soin', 'Rappel de Soin'),
        ('general', 'Notification Générale'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_push'
    )
    type_notification = models.CharField(max_length=50, choices=TYPE_NOTIFICATION)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    # Données contextuelles
    data_contexte = models.JSONField(default=dict, blank=True)
    
    # Pour l'envoi push
    device_token = models.CharField(max_length=500, blank=True)
    envoye = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.utilisateur.email}"

    def marquer_comme_lue(self):
        self.lue = True
        self.save()

    def marquer_comme_envoyee(self):
        self.envoye = True
        self.date_envoi = timezone.now()
        self.save()


class DeviceToken(models.Model):
    """Tokens de notification push pour les appareils."""
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    token = models.CharField(max_length=500, unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=[('ios', 'iOS'), ('android', 'Android'), ('web', 'Web')]
    )
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    dernier_active = models.DateTimeField(auto_now=True)
    nom_appareil = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-dernier_active']

    def __str__(self):
        return f"{self.utilisateur.email} - {self.device_type}"
