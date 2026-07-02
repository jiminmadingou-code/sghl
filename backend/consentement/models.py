from django.db import models
from django.utils import timezone


class ConsentementPatient(models.Model):
    """Gestion du consentement patient (RGPD)."""
    TYPE = [
        ('soins', 'Consentement aux soins'),
        ('donnees', 'Traitement des données personnelles'),
        ('recherche', 'Participation à la recherche'),
        ('partage', 'Partage avec tiers (assurance, etc.)'),
        ('communication', 'Communications marketing'),
    ]
    STATUT = [
        ('accordé', 'Accordé'),
        ('refusé', 'Refusé'),
        ('retiré', 'Retiré'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='consentements')
    type_consentement = models.CharField(max_length=30, choices=TYPE)
    statut = models.CharField(max_length=20, choices=STATUT, default='accordé')
    date_consentement = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(null=True, blank=True)
    date_retrait = models.DateTimeField(null=True, blank=True)
    recueilli_par = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    version_document = models.CharField(max_length=20, default='1.0')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_consentement']
        unique_together = ['patient', 'type_consentement', 'version_document']
        indexes = [models.Index(fields=['patient', 'type_consentement'])]

    def __str__(self):
        return f"{self.patient} — {self.type_consentement} ({self.statut})"

    @property
    def est_actif(self):
        if self.statut != 'accordé':
            return False
        if self.date_expiration and self.date_expiration < timezone.now().date():
            return False
        return True

    def retirer(self, notes=''):
        """Patient retire son consentement."""
        self.statut = 'retiré'
        self.date_retrait = timezone.now()
        if notes:
            self.notes = notes
        self.save()
        from audit.models import AuditTrail
        AuditTrail.log(
            request=None, action_type='UPDATE',
            model_name='ConsentementPatient', object_id=self.pk,
            details={'action': 'Retrait consentement', 'patient_id': self.patient_id}
        )


class DemandeAccesDonnees(models.Model):
    """Demande d'accès ou de suppression des données (droit RGPD)."""
    TYPE = [
        ('acces', 'Droit d\'accès'),
        ('rectification', 'Droit de rectification'),
        ('effacement', 'Droit à l\'effacement'),
        ('portabilite', 'Droit à la portabilité'),
        ('opposition', 'Droit d\'opposition'),
    ]
    STATUT = [
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Traitée', 'Traitée'),
        ('Refusée', 'Refusée'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='demandes_rgpd')
    type_demande = models.CharField(max_length=20, choices=TYPE)
    statut = models.CharField(max_length=20, choices=STATUT, default='En attente')
    description = models.TextField(blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True
    )
    reponse = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_demande']

    def traiter(self, personnel, reponse, statut='Traitée'):
        self.statut = statut
        self.traite_par = personnel
        self.reponse = reponse
        self.date_traitement = timezone.now()
        self.save()
