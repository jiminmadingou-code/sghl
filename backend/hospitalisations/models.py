from django.db import models
from django.conf import settings
from django.utils import timezone
from audit.models import AuditTrail


class Batiment(models.Model):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    adresse = models.TextField(blank=True)
    nombre_etages = models.IntegerField(default=1)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class Service(models.Model):
    batiment = models.ForeignKey(Batiment, on_delete=models.CASCADE, related_name='services')
    code = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    chef_service = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services_diriges'
    )
    actif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['batiment', 'code']
    
    def __str__(self):
        return f"{self.nom} ({self.batiment.nom})"


class Chambre(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='chambres')
    numero = models.CharField(max_length=20)
    type_chambre = models.CharField(
        max_length=20,
        choices=[('Simple', 'Simple'), ('Double', 'Double'), ('Suite', 'Suite')],
        default='Simple'
    )
    tarif_nuitee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['service', 'numero']
    
    def __str__(self):
        return f"{self.service.nom} - {self.numero}"


class Lit(models.Model):
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='lits')
    numero_lit = models.CharField(max_length=10)
    statut = models.CharField(
        max_length=20,
        choices=[('Libre', 'Libre'), ('Occupe', 'Occupé'), ('Indisponible', 'Indisponible')],
        default='Libre'
    )
    equipements = models.JSONField(default=list, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        unique_together = ['chambre', 'numero_lit']

    @property
    def occupe(self):
        return self.statut == 'Occupe'

    def __str__(self):
        return f"{self.chambre} - Lit {self.numero_lit}"


class Hospitalisation(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='hospitalisations')
    lit = models.ForeignKey(Lit, on_delete=models.PROTECT, related_name='hospitalisations')
    medecin_referent = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, related_name='hospitalisations_ref')
    date_entree = models.DateField()
    date_sortie_prevue = models.DateField(null=True, blank=True)
    date_sortie_reelle = models.DateField(null=True, blank=True)
    motif = models.CharField(max_length=255)
    statut = models.CharField(
        max_length=20,
        default='Actif',
        choices=[('Actif', 'Actif'), ('Sorti', 'Sorti'), ('Transféré', 'Transféré')]
    )
    
    # Versioning pour verrouillage optimiste
    version = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_entree']
        indexes = [
            models.Index(fields=['patient', 'statut']),
            models.Index(fields=['statut']),
        ]

    def save(self, *args, **kwargs):
        # Gestion automatique de l'occupation du lit
        if not self.pk:  # Création
            if self.statut == 'Actif' and self.lit.statut != 'Libre':
                raise ValueError("Le lit n'est pas disponible")
            if self.statut == 'Actif':
                self.lit.statut = 'Occupe'
                self.lit.save()
        elif self.has_changed('statut'):
            # Mise à jour occupation lit
            if self.statut == 'Actif':
                self.lit.statut = 'Occupe'
            else:
                self.lit.statut = 'Libre'
            self.lit.save()
        
        # Increment version pour verrouillage optimiste
        if self.pk:
            self.version += 1
        
        super().save(*args, **kwargs)

    def has_changed(self, field):
        """Vérifier si un champ a changé."""
        if not self.pk:
            return True
        old = Hospitalisation.objects.get(pk=self.pk)
        return getattr(old, field) != getattr(self, field)

    def log_audit(self, request, action_type, old_value=None, new_value=None):
        """Créer un log d'audit pour cette hospitalisation."""
        AuditTrail.log(
            request=request,
            action_type=action_type,
            model_name='Hospitalisation',
            object_id=self.pk,
            old_value=old_value,
            new_value=new_value,
            details={'patient_id': self.patient_id}
        )
