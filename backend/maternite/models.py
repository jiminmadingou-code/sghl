from django.db import models
from django.utils import timezone


class Grossesse(models.Model):
    STATUT = [
        ('En cours', 'En cours'),
        ('Accouchée', 'Accouchée'),
        ('Fausse couche', 'Fausse couche'),
        ('Interruption', 'Interruption'),
    ]
    TYPE_GROSSESSE = [('Simple', 'Simple'), ('Gémellaire', 'Gémellaire'), ('Triple', 'Triple')]

    patiente = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='grossesses')
    date_debut_grossesse = models.DateField()
    date_terme_prevue = models.DateField()
    type_grossesse = models.CharField(max_length=20, choices=TYPE_GROSSESSE, default='Simple')
    statut = models.CharField(max_length=20, choices=STATUT, default='En cours')
    medecin_referent = models.ForeignKey(
        'personnel.Personnel', on_delete=models.PROTECT, related_name='grossesses_suivies'
    )
    groupe_sanguin_confirme = models.CharField(max_length=3, blank=True)
    rhesus = models.CharField(max_length=5, blank=True)
    antecedents_obstetricaux = models.TextField(blank=True)
    facteurs_risque = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_debut_grossesse']

    def __str__(self):
        return f"Grossesse {self.patiente} — SA {self.semaines_amenorrhee}"

    @property
    def semaines_amenorrhee(self):
        delta = (timezone.now().date() - self.date_debut_grossesse).days
        return delta // 7


class ConsultationPrenatale(models.Model):
    grossesse = models.ForeignKey(Grossesse, on_delete=models.CASCADE, related_name='consultations_prenatales')
    numero_consultation = models.IntegerField()
    date = models.DateTimeField()
    medecin = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT)
    poids_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tension_systolique = models.IntegerField(null=True, blank=True)
    tension_diastolique = models.IntegerField(null=True, blank=True)
    hauteur_uterine_cm = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bcf = models.IntegerField(null=True, blank=True)  # Bruits du cœur fœtal
    presentation = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    examens_prescrits = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['numero_consultation']
        unique_together = ['grossesse', 'numero_consultation']


class Accouchement(models.Model):
    TYPE = [
        ('Voie basse', 'Voie basse spontanée'),
        ('Forceps', 'Forceps'),
        ('Ventouse', 'Ventouse'),
        ('Césarienne', 'Césarienne programmée'),
        ('Césarienne urgente', 'Césarienne urgente'),
    ]

    grossesse = models.OneToOneField(Grossesse, on_delete=models.PROTECT, related_name='accouchement')
    date_heure = models.DateTimeField()
    type_accouchement = models.CharField(max_length=30, choices=TYPE)
    sage_femme = models.ForeignKey(
        'personnel.Personnel', on_delete=models.PROTECT, related_name='accouchements_sf'
    )
    medecin_present = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='accouchements_med'
    )
    duree_travail_heures = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    complications = models.TextField(blank=True)
    pertes_sanguines_ml = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_heure']


class Nouveau_Ne(models.Model):
    SEXE = [('M', 'Masculin'), ('F', 'Féminin'), ('I', 'Indéterminé')]
    STATUT_VITAL = [('Vivant', 'Vivant'), ('Mort-né', 'Mort-né'), ('Décédé', 'Décédé')]

    accouchement = models.ForeignKey(Accouchement, on_delete=models.CASCADE, related_name='nouveau_nes')
    sexe = models.CharField(max_length=1, choices=SEXE)
    poids_naissance_g = models.IntegerField()
    taille_cm = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    perimetre_cranien_cm = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    score_apgar_1min = models.IntegerField(null=True, blank=True)
    score_apgar_5min = models.IntegerField(null=True, blank=True)
    statut_vital = models.CharField(max_length=10, choices=STATUT_VITAL, default='Vivant')
    anomalies_congenitales = models.TextField(blank=True)
    patient_cree = models.OneToOneField(
        'patients.Patient', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='naissance'
    )

    class Meta:
        ordering = ['accouchement__date_heure']
