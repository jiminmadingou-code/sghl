from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from audit.models import AuditTrail


class Personnel(models.Model):
    ROLES = [
        ('Admin', 'Administrateur'),
        ('Médecin', 'Médecin'),
        ('Infirmier', 'Infirmier'),
        ('Biologiste', 'Biologiste'),
        ('Pharmacien', 'Pharmacien'),
        ('Caissier', 'Caissier'),
        ('Receptionniste', 'Réceptionniste'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personnel')
    role = models.CharField(max_length=20, choices=ROLES)
    service = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    actif = models.BooleanField(default=True)
    
    # MFA
    mfa_active = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True)
    
    # Permissions spécifiques
    permissions = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dernière connexion
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    @property
    def est_medecin(self):
        return self.role == 'Médecin'

    @property
    def est_biologiste(self):
        return self.role == 'Biologiste'

    @property
    def est_admin(self):
        return self.role == 'Admin'

    def has_permission(self, permission):
        """Vérifier si le personnel a une permission spécifique."""
        return permission in self.permissions or self.est_admin

    def log_login(self, ip_address):
        """Log de connexion avec audit."""
        self.last_login_ip = ip_address
        self.last_login_at = timezone.now()
        self.save()
        
        AuditTrail.log(
            request=None,
            action_type='VIEW',
            model_name='Personnel',
            object_id=self.pk,
            details={
                'action': 'Connexion',
                'ip_address': ip_address,
                'user_email': self.user.email
            }
        )


class Permission(models.Model):
    """Permissions granulaires pour RBAC."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    codename = models.CharField(max_length=100, unique=True)
    module = models.CharField(
        max_length=50,
        choices=[
            ('patients', 'Patients'),
            ('hospitalisations', 'Hospitalisations'),
            ('laboratoire', 'Laboratoire'),
            ('pharmacie', 'Pharmacie'),
            ('facturation', 'Facturation'),
            ('personnel', 'Personnel'),
            ('audit', 'Audit'),
            ('dashboard', 'Dashboard'),
        ]
    )

    def __str__(self):
        return f"{self.name} ({self.module})"


class SessionLog(models.Model):
    """Journal des sessions pour audit de sécurité."""
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.CASCADE,
        related_name='session_logs'
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(
        max_length=20,
        choices=[('web', 'Web'), ('mobile', 'Mobile'), ('api', 'API')]
    )
    token_jti = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.personnel.user.email} - {self.date_debut}"

    def fermer(self):
        self.date_fin = timezone.now()
        self.save()
