from django.db import models
from django.utils import timezone


class SalleOperation(models.Model):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    service = models.ForeignKey('hospitalisations.Service', on_delete=models.PROTECT)
    equipements = models.JSONField(default=list, blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} — {self.nom}"


class InterventionChirurgicale(models.Model):
    STATUT = [
        ('Programmée', 'Programmée'),
        ('En cours', 'En cours'),
        ('Terminée', 'Terminée'),
        ('Annulée', 'Annulée'),
        ('Reportée', 'Reportée'),
    ]
    URGENCE = [('Programmée', 'Programmée'), ('Urgente', 'Urgente'), ('Semi-urgente', 'Semi-urgente')]
    TYPE_ANESTHESIE = [
        ('Générale', 'Anesthésie générale'),
        ('Locorégionale', 'Anesthésie locorégionale'),
        ('Locale', 'Anesthésie locale'),
        ('Rachianesthésie', 'Rachianesthésie'),
        ('Péridurale', 'Péridurale'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='interventions_chirurgicales')
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation', on_delete=models.PROTECT, related_name='interventions_chirurgicales'
    )
    salle = models.ForeignKey(SalleOperation, on_delete=models.PROTECT, related_name='interventions')

    chirurgien_principal = models.ForeignKey(
        'personnel.Personnel', on_delete=models.PROTECT, related_name='interventions_chirurgien'
    )
    chirurgien_aide = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interventions_aide'
    )
    anesthesiste = models.ForeignKey(
        'personnel.Personnel', on_delete=models.PROTECT, related_name='interventions_anesthesiste'
    )
    infirmier_bloc = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interventions_infirmier'
    )

    acte_principal = models.CharField(max_length=200)
    code_ccam = models.CharField(max_length=20, blank=True)  # Code CCAM français
    actes_associes = models.JSONField(default=list, blank=True)
    type_urgence = models.CharField(max_length=20, choices=URGENCE, default='Programmée')
    type_anesthesie = models.CharField(max_length=20, choices=TYPE_ANESTHESIE)

    date_programmee = models.DateTimeField()
    date_debut_reelle = models.DateTimeField(null=True, blank=True)
    date_fin_reelle = models.DateTimeField(null=True, blank=True)
    duree_prevue_minutes = models.IntegerField(default=60)

    statut = models.CharField(max_length=20, choices=STATUT, default='Programmée')

    # Compte-rendu opératoire
    compte_rendu_operatoire = models.TextField(blank=True)
    complications = models.TextField(blank=True)
    pertes_sanguines_ml = models.IntegerField(null=True, blank=True)
    transfusions = models.JSONField(default=list, blank=True)

    # Suites opératoires
    consignes_postop = models.TextField(blank=True)
    destination_postop = models.CharField(
        max_length=50,
        choices=[('SSPI', 'SSPI'), ('Réanimation', 'Réanimation'), ('Service', 'Service'), ('Domicile', 'Domicile')],
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_programmee']
        indexes = [
            models.Index(fields=['statut', 'date_programmee']),
            models.Index(fields=['patient', '-date_programmee']),
        ]

    def __str__(self):
        return f"{self.acte_principal} — {self.patient} ({self.date_programmee.date()})"

    @property
    def duree_reelle_minutes(self):
        if self.date_debut_reelle and self.date_fin_reelle:
            return int((self.date_fin_reelle - self.date_debut_reelle).total_seconds() / 60)
        return None

    def demarrer(self):
        self.statut = 'En cours'
        self.date_debut_reelle = timezone.now()
        self.save()

    def terminer(self, compte_rendu='', complications=''):
        self.statut = 'Terminée'
        self.date_fin_reelle = timezone.now()
        self.compte_rendu_operatoire = compte_rendu
        self.complications = complications
        self.save()
