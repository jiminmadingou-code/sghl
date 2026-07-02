from django.db import models
from django.utils import timezone


class RendezVous(models.Model):
    STATUT = [
        ('En attente', 'En attente'),
        ('Confirmé', 'Confirmé'),
        ('Annulé', 'Annulé'),
        ('Terminé', 'Terminé'),
        ('Absent', 'Absent'),
    ]
    TYPE = [
        ('Consultation', 'Consultation'),
        ('Suivi', 'Suivi'),
        ('Urgence', 'Urgence'),
        ('Téléconsultation', 'Téléconsultation'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='rendez_vous')
    medecin = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, related_name='rendez_vous')
    disponibilite = models.ForeignKey(
        'gardes.DisponibiliteMedecin',
        on_delete=models.PROTECT,
        related_name='rendez_vous',
        null=True, blank=True
    )
    date_heure = models.DateTimeField()
    duree_minutes = models.IntegerField(default=30)
    type_rdv = models.CharField(max_length=20, choices=TYPE, default='Consultation')
    motif = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUT, default='En attente')
    notes = models.TextField(blank=True)

    # Confirmation
    confirmation_envoyee = models.BooleanField(default=False)
    rappel_envoye = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_heure']
        indexes = [
            models.Index(fields=['medecin', 'date_heure']),
            models.Index(fields=['patient', '-date_heure']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.patient} - Dr {self.medecin} le {self.date_heure}"

    def confirmer(self):
        self.statut = 'Confirmé'
        self.save()
        self._envoyer_confirmation()

    def annuler(self, motif=''):
        self.statut = 'Annulé'
        if motif:
            self.notes = motif
        self.save()

    def _envoyer_confirmation(self):
        """Envoyer email de confirmation au patient."""
        try:
            from email_service.services import send_appointment_reminder
            patient = self.patient
            if hasattr(patient, 'email') and patient.email:
                details = f"{self.type_rdv} le {self.date_heure.strftime('%d/%m/%Y à %H:%M')} avec Dr {self.medecin}"
                send_appointment_reminder(patient.email, str(patient), details)
                self.confirmation_envoyee = True
                self.save(update_fields=['confirmation_envoyee'])
        except Exception:
            pass
