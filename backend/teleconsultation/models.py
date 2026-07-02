from django.db import models
from django.utils import timezone


class SessionTeleconsultation(models.Model):
    STATUT = [
        ('Planifiée', 'Planifiée'),
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Terminée', 'Terminée'),
        ('Annulée', 'Annulée'),
        ('Absent', 'Patient absent'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='teleconsultations')
    medecin = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, related_name='teleconsultations')
    rendez_vous = models.OneToOneField(
        'rendez_vous.RendezVous', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teleconsultation'
    )

    date_heure_prevue = models.DateTimeField()
    date_debut_reelle = models.DateTimeField(null=True, blank=True)
    date_fin_reelle = models.DateTimeField(null=True, blank=True)

    statut = models.CharField(max_length=20, choices=STATUT, default='Planifiée')
    motif = models.CharField(max_length=255)

    # Lien de connexion sécurisé
    lien_patient = models.CharField(max_length=255, blank=True)
    lien_medecin = models.CharField(max_length=255, blank=True)
    token_session = models.CharField(max_length=64, unique=True, blank=True)

    # Compte-rendu
    notes_consultation = models.TextField(blank=True)
    diagnostic = models.CharField(max_length=255, blank=True)
    prescription_generee = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_heure_prevue']
        indexes = [
            models.Index(fields=['statut', 'date_heure_prevue']),
            models.Index(fields=['medecin', 'date_heure_prevue']),
        ]

    def __str__(self):
        return f"Téléconsultation {self.patient} — Dr {self.medecin} ({self.date_heure_prevue})"

    def generer_liens(self):
        import secrets
        self.token_session = secrets.token_hex(32)
        base = f"/teleconsultation/{self.token_session}"
        self.lien_patient = f"{base}/patient"
        self.lien_medecin = f"{base}/medecin"
        self.save()

    def demarrer(self):
        self.statut = 'En cours'
        self.date_debut_reelle = timezone.now()
        self.save()

    def terminer(self, notes='', diagnostic=''):
        self.statut = 'Terminée'
        self.date_fin_reelle = timezone.now()
        self.notes_consultation = notes
        self.diagnostic = diagnostic
        self.save()

    @property
    def duree_minutes(self):
        if self.date_debut_reelle and self.date_fin_reelle:
            return int((self.date_fin_reelle - self.date_debut_reelle).total_seconds() / 60)
        return None
