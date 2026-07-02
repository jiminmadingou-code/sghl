from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class EmailTemplate(models.Model):
    """Modèles d'emails pré-définis"""
    NOM = [
        ('welcome', 'Bienvenue'),
        ('password_reset', 'Réinitialisation mot de passe'),
        ('appointment_reminder', 'Rappel rendez-vous'),
        ('lab_results', 'Résultats laboratoire disponibles'),
        ('prescription_ready', 'Ordonnance prête'),
        ('invoice_generated', 'Facture générée'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(max_length=50, choices=NOM, unique=True)
    subject = models.CharField(max_length=200)
    html_template = models.TextField(help_text="Template HTML avec variables {var}")
    text_template = models.TextField(help_text="Template texte avec variables {var}")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Template Email"
        verbose_name_plural = "Templates Email"
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def render(self, context: dict):
        """Rendre le template avec le contexte fourni"""
        html = self.html_template
        text = self.text_template
        
        for key, value in context.items():
            html = html.replace(f'{{{key}}}', str(value))
            text = text.replace(f'{{{key}}}', str(value))
        
        return html, text


class EmailLog(models.Model):
    """Journal d'envoi des emails pour audit"""
    STATUS = [
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
        ('bounced', 'Rejeté'),
    ]
    
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Liens avec le système
    patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True)
    personnel = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log Email"
        verbose_name_plural = "Logs Email"
    
    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})"


class EmailQueue(models.Model):
    """File d'attente pour envoi asynchrone"""
    STATUS = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
    ]
    
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True)
    personnel = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_at', '-created_at']
        verbose_name = "File d'attente Email"
        verbose_name_plural = "Files d'attente Email"
    
    def __str__(self):
        return f"{self.recipient} - {self.subject}"
    
    def can_retry(self):
        return self.retry_count < self.max_retries


def send_transactional_email(
    recipient: str,
    subject: str,
    html_content: str,
    text_content: str = None,
    patient=None,
    personnel=None,
    template=None,
    send_async: bool = True
):
    """
    Envoyer un email transactionnel
    
    Args:
        recipient: Adresse email du destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML
        text_content: Contenu texte (optionnel)
        patient: Patient lié (optionnel)
        personnel: Personnel lié (optionnel)
        template: Template utilisé (optionnel)
        send_async: Envoyer asynchrone via file (défaut True)
    
    Returns:
        EmailLog ou EmailQueue selon send_async
    """
    # Créer le log
    email_log = EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        html_content=html_content,
        text_content=text_content or html_content,
        patient=patient,
        personnel=personnel,
        template=template
    )
    
    if send_async:
        # Mettre en file d'attente
        email_queue = EmailQueue.objects.create(
            recipient=recipient,
            subject=subject,
            html_content=html_content,
            text_content=text_content or html_content,
            patient=patient,
            personnel=personnel,
            template=template
        )
        logger.info(f"Email mis en file d'attente: {email_queue.id}")
        return email_queue
    else:
        # Envoyer immédiatement
        try:
            send_mail(
                subject=subject,
                message=text_content or html_content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient],
                html_message=html_content,
                fail_silently=False
            )
            
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.save()
            
            logger.info(f"Email envoyé avec succès: {recipient}")
            return email_log
            
        except Exception as e:
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save()
            logger.error(f"Échec envoi email: {e}")
            raise
