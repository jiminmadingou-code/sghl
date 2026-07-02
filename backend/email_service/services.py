"""
Service d'envoi d'emails asynchrones
Utilise Django's mail backend avec file d'attente
"""
import smtplib
import logging
from django.core.mail import get_connection
from django.conf import settings
from django.utils import timezone
from .models import EmailQueue, EmailLog

logger = logging.getLogger(__name__)


class EmailWorker:
    """Worker pour traiter la file d'attente d'emails"""
    
    @staticmethod
    def process_queue(max_emails: int = 100):
        """
        Traiter les emails en attente
        
        Args:
            max_emails: Nombre maximum d'emails à traiter par cycle
        """
        # Récupérer les emails en attente
        pending_emails = EmailQueue.objects.filter(
            status='pending',
            scheduled_at__lte=timezone.now()
        )[:max_emails]
        
        processed = 0
        for email_queue in pending_emails:
            try:
                EmailWorker._send_email(email_queue)
                processed += 1
            except Exception as e:
                logger.error(f"Erreur envoi email {email_queue.id}: {e}")
                EmailWorker._handle_failure(email_queue, str(e))
        
        logger.info(f"Traité {processed} emails")
        return processed
    
    @staticmethod
    def _send_email(email_queue: EmailQueue):
        """Envoyer un email individuel"""
        email_queue.status = 'processing'
        email_queue.save()
        
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            fail_silently=False
        )
        
        msg = connection.create_message()
        msg.from_email = settings.EMAIL_HOST_USER
        msg.to = [email_queue.recipient]
        msg.subject = email_queue.subject
        msg.body = email_queue.text_content
        msg.attach_alternative(email_queue.html_content, "text/html")
        
        connection.send_messages([msg])
        
        # Mettre à jour le statut
        email_queue.status = 'sent'
        email_queue.sent_at = timezone.now()
        email_queue.save()
        
        # Mettre à jour le log
        try:
            email_log = EmailLog.objects.filter(
                recipient=email_queue.recipient,
                subject=email_queue.subject
            ).order_by('-created_at').first()
            if email_log:
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
                email_log.save()
        except Exception as e:
            logger.warning(f"Impossible de mettre à jour le log: {e}")
        
        logger.info(f"Email envoyé: {email_queue.recipient}")
    
    @staticmethod
    def _handle_failure(email_queue: EmailQueue, error: str):
        """Gérer un échec d'envoi"""
        email_queue.retry_count += 1
        email_queue.error_message = error
        
        if email_queue.can_retry():
            # Programmer le réessai avec backoff exponentiel
            from datetime import timedelta
            retry_delay = timedelta(minutes=5 * (2 ** email_queue.retry_count))
            email_queue.scheduled_at = timezone.now() + retry_delay
            email_queue.status = 'pending'
            email_queue.save()
            logger.info(f"Réessai programmé pour email {email_queue.id}")
        else:
            email_queue.status = 'failed'
            email_queue.save()
            
            # Mettre à jour le log
            try:
                email_log = EmailLog.objects.filter(
                    recipient=email_queue.recipient,
                    subject=email_queue.subject
                ).order_by('-created_at').first()
                if email_log:
                    email_log.status = 'failed'
                    email_log.error_message = error
                    email_log.save()
            except Exception as e:
                logger.warning(f"Impossible de mettre à jour le log: {e}")
            
            logger.error(f"Email échoué après {email_queue.max_retries} tentatives: {email_queue.id}")


def send_welcome_email(patient_email: str, patient_name: str):
    """Envoyer email de bienvenue"""
    from .models import EmailTemplate
    
    template = EmailTemplate.objects.filter(name='welcome').first()
    if not template:
        logger.warning("Template 'welcome' non trouvé")
        return
    
    context = {
        'patient_name': patient_name,
    }
    
    html, text = template.render(context)
    
    from .models import send_transactional_email
    return send_transactional_email(
        recipient=patient_email,
        subject=template.subject,
        html_content=html,
        text_content=text,
        template=template
    )


def send_password_reset_email(user_email: str, reset_link: str):
    """Envoyer email de réinitialisation de mot de passe"""
    from .models import EmailTemplate
    
    template = EmailTemplate.objects.filter(name='password_reset').first()
    if not template:
        logger.warning("Template 'password_reset' non trouvé")
        return
    
    context = {
        'reset_link': reset_link,
    }
    
    html, text = template.render(context)
    
    from .models import send_transactional_email
    return send_transactional_email(
        recipient=user_email,
        subject=template.subject,
        html_content=html,
        text_content=text,
        template=template
    )


def send_appointment_reminder(patient_email: str, patient_name: str, appointment_details: str):
    """Envoyer rappel de rendez-vous"""
    from .models import EmailTemplate
    
    template = EmailTemplate.objects.filter(name='appointment_reminder').first()
    if not template:
        logger.warning("Template 'appointment_reminder' non trouvé")
        return
    
    context = {
        'patient_name': patient_name,
        'appointment_details': appointment_details,
    }
    
    html, text = template.render(context)
    
    from .models import send_transactional_email
    return send_transactional_email(
        recipient=patient_email,
        subject=template.subject,
        html_content=html,
        text_content=text,
        template=template
    )


def send_lab_results_notification(patient_email: str, patient_name: str, examination_count: int):
    """Notifier patient que résultats labo sont disponibles"""
    from .models import EmailTemplate
    
    template = EmailTemplate.objects.filter(name='lab_results').first()
    if not template:
        logger.warning("Template 'lab_results' non trouvé")
        return
    
    context = {
        'patient_name': patient_name,
        'examination_count': examination_count,
    }
    
    html, text = template.render(context)
    
    from .models import send_transactional_email
    return send_transactional_email(
        recipient=patient_email,
        subject=template.subject,
        html_content=html,
        text_content=text,
        template=template
    )


def send_invoice_notification(patient_email: str, patient_name: str, invoice_number: str, amount: str):
    """Notifier patient qu'une facture est générée"""
    from .models import EmailTemplate
    
    template = EmailTemplate.objects.filter(name='invoice_generated').first()
    if not template:
        logger.warning("Template 'invoice_generated' non trouvé")
        return
    
    context = {
        'patient_name': patient_name,
        'invoice_number': invoice_number,
        'amount': amount,
    }
    
    html, text = template.render(context)
    
    from .models import send_transactional_email
    return send_transactional_email(
        recipient=patient_email,
        subject=template.subject,
        html_content=html,
        text_content=text,
        template=template
    )
