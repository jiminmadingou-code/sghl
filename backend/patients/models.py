from django.db import models
from django.conf import settings
from django.utils import timezone
from audit.models import AuditTrail
from core.security import AESCipher


class Patient(models.Model):
    SEXE = [('M', 'Masculin'), ('F', 'Féminin')]
    GROUPE_SANGUIN = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]

    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN, blank=True)
    allergies = models.TextField(blank=True)
    antecedents = models.TextField(blank=True)
    
    # Données sensibles chiffrées
    numero_securise = models.CharField(max_length=50, unique=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Versioning
    version = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nom', 'prenom']),
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def save(self, *args, **kwargs):
        # Générer un numéro sécurisé unique
        if not self.numero_securise:
            import hashlib
            self.numero_securise = hashlib.sha256(
                f"{self.date_naissance}{self.nom}{self.prenom}".encode()
            ).hexdigest()[:16]

        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)

    def log_access(self, user, ip_address=None):
        """Log de l'accès au dossier patient."""
        AuditTrail.log(
            request=None,
            action_type='VIEW',
            model_name='Patient',
            object_id=self.pk,
            details={
                'user_id': user.id if hasattr(user, 'id') else None,
                'user_email': user.email if hasattr(user, 'email') else None,
                'ip_address': ip_address,
                'action': 'Consultation dossier patient'
            }
        )

    def anonymiser(self):
        """Anonymiser les données du patient pour usage statistique."""
        import uuid
        self.numero_securise = str(uuid.uuid4())
        self.nom = f"Anonyme_{self.numero_securise[:8]}"
        self.prenom = ""
        self.telephone = ""
        self.adresse = ""
        self.save()


class Consultation(models.Model):
    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Terminée', 'Terminée'),
        ('Validée', 'Validée'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='consultations')
    medecin = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, related_name='consultations_med')
    date = models.DateTimeField()
    motif = models.CharField(max_length=255)
    diagnostic_cim10 = models.CharField(max_length=10, blank=True)
    diagnostic_libelle = models.CharField(max_length=255, blank=True)
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    statut = models.CharField(max_length=20, default='En attente', choices=STATUT_CHOICES)
    
    # Signature électronique
    signe_par = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations_signees'
    )
    date_signature = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Immuabilité après validation
    verrouille = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['statut']),
        ]

    def valider(self, medecin):
        """Valider et verrouiller la consultation."""
        from django.utils import timezone
        self.statut = 'Validée'
        self.signe_par = medecin
        self.date_signature = timezone.now()
        self.verrouille = True
        self.save()

    def log_audit(self, request, action_type, old_value=None, new_value=None):
        """Créer un log d'audit."""
        AuditTrail.log(
            request=request,
            action_type=action_type,
            model_name='Consultation',
            object_id=self.pk,
            old_value=old_value,
            new_value=new_value,
            details={'patient_id': self.patient_id}
        )
