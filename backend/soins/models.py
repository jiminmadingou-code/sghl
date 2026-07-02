from django.db import models
from django.conf import settings
from datetime import datetime, time
from django.core.validators import MinValueValidator, MaxValueValidator


class TypeSoin(models.Model):
    """Types de soins planifiables."""
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duree_estimee_minutes = models.IntegerField(default=15)
    categorie = models.CharField(max_length=100, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Type de soin'
        verbose_name_plural = 'Types de soins'

    def __str__(self):
        return f"{self.code} - {self.nom}"


class PlanificationSoins(models.Model):
    """Planification des soins pour un patient hospitalisé."""
    STATUT_CHOICES = [
        ('Planifié', 'Planifié'),
        ('En cours', 'En cours'),
        ('Terminé', 'Terminé'),
        ('Annulé', 'Annulé'),
        ('Omis', 'Omis'),
    ]

    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation',
        on_delete=models.CASCADE,
        related_name='soins_planifies'
    )
    type_soin = models.ForeignKey(TypeSoin, on_delete=models.PROTECT)
    prescription_medical = models.ForeignKey(
        'prescriptions.Prescription',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='soins_associes'
    )
    infirmier_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='soins_a_realiser',
        limit_choices_to={'is_staff': True}
    )
    date_heure_prevue = models.DateTimeField()
    duree_prevue_minutes = models.IntegerField(default=15)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='Planifié')
    priorite = models.CharField(
        max_length=10,
        choices=[('Normale', 'Normale'), ('Urgente', 'Urgente'), ('Haute', 'Haute')],
        default='Normale'
    )
    instructions = models.TextField(blank=True)
    
    # Suivi de réalisation
    date_heure_reelle = models.DateTimeField(null=True, blank=True)
    notes_realisation = models.TextField(blank=True)
    realise_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='soins_realises',
        limit_choices_to={'is_staff': True}
    )
    
    # Alertes
    alerte_omission = models.BooleanField(default=False)
    date_dernier_rappel = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['date_heure_prevue']
        indexes = [
            models.Index(fields=['hospitalisation', 'statut']),
            models.Index(fields=['date_heure_prevue', 'statut']),
        ]

    def __str__(self):
        return f"{self.type_soin.nom} - {self.hospitalisation.patient.nom} ({self.date_heure_prevue})"

    def marquer_comme_realise(self, infirmier, notes=''):
        """Marquer le soin comme réalisé."""
        from django.utils import timezone
        self.statut = 'Terminé'
        self.date_heure_reelle = timezone.now()
        self.realise_par = infirmier
        self.notes_realisation = notes
        self.save()

    def marquer_comme_omis(self):
        """Marquer le soin comme omis (alerte)."""
        self.statut = 'Omis'
        self.alerte_omission = True
        self.save()


class ConstanteVitale(models.Model):
    """Enregistrement des constantes vitales d'un patient."""
    TYPE_CHOICES = [
        ('Temperature', 'Température (°C)'),
        ('Pouls', 'Pouls (bpm)'),
        ('PressionSystolique', 'Pression Artérielle Systolique (mmHg)'),
        ('PressionDiastolique', 'Pression Artérielle Diastolique (mmHg)'),
        ('Respiration', 'Fréquence Respiratoire (min⁻¹)'),
        ('SaturationO2', 'Saturation en O2 (%)'),
        ('Glycemie', 'Glycémie (mg/dL)'),
        ('Poids', 'Poids (kg)'),
        ('Taille', 'Taille (cm)'),
        ('IMC', 'Indice de Masse Corporelle'),
    ]

    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation',
        on_delete=models.CASCADE,
        related_name='constantsvitales'
    )
    type_constante = models.CharField(max_length=50, choices=TYPE_CHOICES)
    valeur = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unite = models.CharField(max_length=20, blank=True)
    mesure_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='constantes_mesurees'
    )
    date_mesure = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    # Alertes
    alerte_seuil = models.BooleanField(default=False)
    seuil_bas = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    seuil_haut = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-date_mesure']
        indexes = [
            models.Index(fields=['hospitalisation', 'type_constante', '-date_mesure']),
        ]

    def __str__(self):
        return f"{self.hospitalisation.patient.nom} - {self.type_constante}: {self.valeur}"

    def verifier_seuils(self):
        """Vérifier si la valeur est dans les seuils normaux."""
        if self.seuil_bas and self.valeur < self.seuil_bas:
            self.alerte_seuil = True
            self.save()
            return 'BAS'
        if self.seuil_haut and self.valeur > self.seuil_haut:
            self.alerte_seuil = True
            self.save()
            return 'HAUT'
        return 'NORMAL'

    def save(self, *args, **kwargs):
        # Définition des seuils par défaut selon le type
        if not self.seuil_bas and not self.seuil_haut:
            seuils = {
                'Temperature': (36.0, 38.0),
                'Pouls': (60, 100),
                'PressionSystolique': (90, 140),
                'PressionDiastolique': (60, 90),
                'Respiration': (12, 20),
                'SaturationO2': (95, 100),
                'Glycemie': (70, 140),
            }
            if self.type_constante in seuils:
                self.seuil_bas, self.seuil_haut = seuils[self.type_constante]
        
        super().save(*args, **kwargs)
        self.verifier_seuils()


class InterventionInfirmiere(models.Model):
    """Historique complet des interventions infirmières."""
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation',
        on_delete=models.CASCADE,
        related_name='interventions'
    )
    infirmier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='interventions'
    )
    date_heure = models.DateTimeField(auto_now_add=True)
    type_intervention = models.CharField(max_length=100)
    description = models.TextField()
    medicaments_administres = models.JSONField(default=list, blank=True)
    reponse_patient = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_heure']

    def __str__(self):
        return f"{self.hospitalisation.patient.nom} - {self.type_intervention} ({self.date_heure})"
