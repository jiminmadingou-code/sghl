"""
Gestion des plannings de garde et planification
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from datetime import time, timedelta
from django.utils import timezone


class TypeGarde(models.Model):
    """Types de gardes."""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    duree_heures = models.IntegerField(default=12)
    coefficient_paiement = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.5)]
    )

    def __str__(self):
        return self.nom


class PlanningGarde(models.Model):
    """Planning de garde pour le personnel."""
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('confirmé', 'Confirmé'),
        ('annule', 'Annulé'),
        ('remplace', 'Remplacé'),
    ]

    personnel = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.CASCADE,
        related_name='plannings_garde'
    )
    type_garde = models.ForeignKey(TypeGarde, on_delete=models.PROTECT)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    lieu = models.CharField(max_length=200, blank=True)
    observations = models.TextField(blank=True)
    
    # Remplacement
    remplace_planning = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='remplacements_recus'
    )
    remplace_par = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='remplacements_effectues'
    )
    
    # Validation
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gardes_validees'
    )
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['date_debut']
        indexes = [
            models.Index(fields=['personnel', '-date_debut']),
            models.Index(fields=['statut']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_fin__gt=models.F('date_debut')),
                name='date_fin_apres_debut'
            ),
        ]

    def __str__(self):
        return f"{self.personnel.user.get_full_name()} - {self.type_garde.nom} ({self.date_debut})"

    def clean(self):
        """Validation des dates et chevauchements."""
        if self.date_fin <= self.date_debut:
            raise ValidationError("La date de fin doit être après la date de début")
        
        # Vérifier les chevauchements
        if self.pk:
            existing = PlanningGarde.objects.filter(
                personnel=self.personnel
            ).exclude(pk=self.pk)
        else:
            existing = PlanningGarde.objects.filter(personnel=self.personnel)
        
        if existing.filter(
            models.Q(date_debut__lt=self.date_fin) & models.Q(date_fin__gt=self.date_debut)
        ).exists():
            raise ValidationError("Chevauchement de garde détecté")

    def confirmer(self, validateur=None):
        """Confirmer le planning de garde."""
        self.statut = 'confirmé'
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()

    def annuler(self, motif=''):
        """Annuler le planning de garde."""
        self.statut = 'annule'
        self.observations = motif
        self.save()


class Astreinte(models.Model):
    """Astreinte (disponibilité téléphonique/outre-site)."""
    personnel = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.CASCADE,
        related_name='astreintes'
    )
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    type_contact = models.CharField(
        max_length=20,
        choices=[('telephonique', 'Téléphonique'), ('physique', 'Sur place')]
    )
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['date_debut']

    def __str__(self):
        return f"{self.personnel.nom} - Astreinte ({self.date_debut})"


class DisponibiliteMedecin(models.Model):
    """Disponibilités des médecins pour rendez-vous."""
    medecin = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.CASCADE,
        related_name='disponibilites'
    )
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    duree_consultation_minutes = models.IntegerField(default=30)
    creneaux_disponibles = models.IntegerField(default=0)
    exceptionnelle = models.BooleanField(default=False)
    motif_exception = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['date', 'heure_debut']
        unique_together = ['medecin', 'date', 'heure_debut']

    def __str__(self):
        return f"{self.medecin.user.get_full_name()} - {self.date} ({self.heure_debut}-{self.heure_fin})"

    def calculer_creneaux(self):
        """Calculer le nombre de créneaux disponibles."""
        debut = timezone.datetime.combine(timezone.now().date(), self.heure_debut)
        fin = timezone.datetime.combine(timezone.now().date(), self.heure_fin)
        duree_totale = (fin - debut).seconds // 60
        self.creneaux_disponibles = duree_totale // self.duree_consultation_minutes
        self.save()
        return self.creneaux_disponibles


class CongesAbsence(models.Model):
    """Gestion des congés et absences du personnel."""
    TYPE_ABSENCE = [
        ('conge_paye', 'Congés Payés'),
        ('maladie', 'Maladie'),
        ('congematernal', 'Congé Maternité'),
        ('congeparental', 'Congé Parental'),
        ('autorisation', 'Autorisation d\'Absence'),
        ('autre', 'Autre'),
    ]

    personnel = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.CASCADE,
        related_name='absences'
    )
    type_absence = models.CharField(max_length=50, choices=TYPE_ABSENCE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(
        max_length=20,
        choices=[('demande', 'Demandé'), ('accepte', 'Accepté'), ('refuse', 'Refusé')],
        default='demande'
    )
    motif = models.TextField(blank=True)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='absences_validees'
    )
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.personnel.nom} - {self.type_absence} ({self.date_debut} au {self.date_fin})"

    def accepter(self, validateur):
        self.statut = 'accepté'
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()

    def refuser(self, validateur, motif_refus=''):
        self.statut = 'refusé'
        self.valide_par = validateur
        self.motif = motif_refus
        self.date_validation = timezone.now()
        self.save()
