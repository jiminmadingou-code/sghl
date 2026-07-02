"""
Modèles pour le Dashboard Administratif et KPIs
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class KPICache(models.Model):
    """Cache pour les KPIs calculés (optimisation performance)."""
    key = models.CharField(max_length=200, unique=True)
    value = models.JSONField()
    calculated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'KPI Cache'
        verbose_name_plural = 'KPI Caches'

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def get_or_calculate(cls, key, calculation_func, ttl_hours=1):
        """
        Récupérer un KPI depuis le cache ou le recalculer.
        """
        try:
            cache_entry = cls.objects.get(key=key)
            if not cache_entry.is_expired():
                return cache_entry.value
        except cls.DoesNotExist:
            pass
        
        # Calculer la valeur
        value = calculation_func()
        
        # Sauvegarder dans le cache
        expires_at = timezone.now() + timedelta(hours=ttl_hours)
        cache_entry, _ = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'expires_at': expires_at}
        )
        
        return value


class SystemHealthLog(models.Model):
    """Logs de santé du système pour monitoring."""
    CHECK_TYPE = [
        ('database', 'Base de Données'),
        ('cache', 'Cache Redis'),
        ('storage', 'Stockage Fichiers'),
        ('email', 'Service Email'),
        ('api_response', 'Temps de Réponse API'),
        ('disk_space', 'Espace Disque'),
        ('memory', 'Mémoire Système'),
    ]

    check_type = models.CharField(max_length=50, choices=CHECK_TYPE)
    status = models.CharField(
        max_length=20,
        choices=[('OK', 'OK'), ('WARNING', 'Alerte'), ('ERROR', 'Erreur')]
    )
    message = models.TextField(blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['check_type', '-checked_at']),
        ]

    def __str__(self):
        return f"{self.check_type} - {self.status} ({self.checked_at})"


class NotificationSysteme(models.Model):
    """Notifications système et alertes."""
    PRIORITY = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('critical', 'Critique'),
    ]

    TYPE_NOTIFICATION = [
        ('alerte_stock', 'Alerte Stock Pharmacie'),
        ('alerte_patient', 'Alerte Patient'),
        ('alerte_resultat', 'Alerte Résultat Laboratoire'),
        ('gardiemodification', 'Modification de Garde'),
        ('systeme', 'Notification Système'),
        ('facturation', 'Alerte Facturation'),
    ]

    titre = models.CharField(max_length=200)
    type_notification = models.CharField(max_length=50, choices=TYPE_NOTIFICATION)
    description = models.TextField()
    priorite = models.CharField(max_length=20, choices=PRIORITY, default='medium')
    lu = models.BooleanField(default=False)
    lu_par = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_lues'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    # Cible spécifique
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    class Meta:
        ordering = ['-date_creation', '-priorite']

    def __str__(self):
        return f"{self.titre} ({self.priorite})"


class SessionActif(models.Model):
    """Suivi des sessions actives pour monitoring et sécurité."""
    user = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.CASCADE,
        related_name='sessions_actives'
    )
    token_jti = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_activite = models.DateTimeField(auto_now=True)
    device_type = models.CharField(
        max_length=20,
        choices=[('web', 'Web'), ('mobile', 'Mobile'), ('api', 'API')]
    )

    class Meta:
        ordering = ['-date_derniere_activite']

    def __str__(self):
        return f"{self.user.email} - {self.device_type} ({self.ip_address})"
