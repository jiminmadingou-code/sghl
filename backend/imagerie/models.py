from django.db import models
from django.utils import timezone


class Modalite(models.Model):
    """Modalités d'imagerie disponibles."""
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} — {self.nom}"


class ExamenImagerie(models.Model):
    STATUT = [
        ('Prescrit', 'Prescrit'),
        ('Planifié', 'Planifié'),
        ('En cours', 'En cours'),
        ('Réalisé', 'Réalisé'),
        ('Interprété', 'Interprété'),
        ('Validé', 'Validé'),
        ('Annulé', 'Annulé'),
    ]
    URGENCE = [('Normal', 'Normal'), ('Urgent', 'Urgent'), ('STAT', 'STAT — Immédiat')]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='examens_imagerie')
    modalite = models.ForeignKey(Modalite, on_delete=models.PROTECT)
    prescripteur = models.ForeignKey(
        'personnel.Personnel', on_delete=models.PROTECT, related_name='imageries_prescrites'
    )
    radiologue = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='imageries_interpretees'
    )
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='examens_imagerie'
    )

    region_anatomique = models.CharField(max_length=100)
    indication_clinique = models.TextField()
    urgence = models.CharField(max_length=10, choices=URGENCE, default='Normal')
    statut = models.CharField(max_length=20, choices=STATUT, default='Prescrit')

    date_prescription = models.DateTimeField(auto_now_add=True)
    date_realisation = models.DateTimeField(null=True, blank=True)
    date_interpretation = models.DateTimeField(null=True, blank=True)

    # Compte-rendu
    compte_rendu = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    rapport_pdf = models.FileField(upload_to='imagerie/rapports/', null=True, blank=True)

    # Immuabilité après validation
    valide_par = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='imageries_validees'
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    verrouille = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_prescription']
        indexes = [
            models.Index(fields=['patient', '-date_prescription']),
            models.Index(fields=['statut', 'urgence']),
        ]

    def __str__(self):
        return f"{self.modalite.code} — {self.patient} ({self.statut})"

    def valider(self, radiologue):
        self.statut = 'Validé'
        self.valide_par = radiologue
        self.date_validation = timezone.now()
        self.verrouille = True
        self.save()


class ImageDICOM(models.Model):
    """Images DICOM associées à un examen."""
    examen = models.ForeignKey(ExamenImagerie, on_delete=models.CASCADE, related_name='images')
    fichier = models.FileField(upload_to='imagerie/dicom/')
    serie = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200, blank=True)
    taille_octets = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, default='application/dicom')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']
