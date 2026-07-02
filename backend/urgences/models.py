from django.db import models
from django.utils import timezone


class PassageUrgences(models.Model):
    TRIAGE = [
        ('P1', 'P1 — Urgence absolue (rouge)'),
        ('P2', 'P2 — Urgence relative (orange)'),
        ('P3', 'P3 — Urgence différée (jaune)'),
        ('P4', 'P4 — Non urgent (vert)'),
        ('P5', 'P5 — Décédé (noir)'),
    ]
    STATUT = [
        ('Triage', 'Triage'),
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Hospitalisé', 'Hospitalisé'),
        ('Sorti', 'Sorti'),
        ('Transféré', 'Transféré'),
        ('Décédé', 'Décédé'),
    ]
    MODE_ARRIVEE = [
        ('Ambulance', 'Ambulance'),
        ('SMUR', 'SMUR'),
        ('Pompiers', 'Pompiers'),
        ('Autonome', 'Autonome'),
        ('Hélicoptère', 'Hélicoptère'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='passages_urgences')
    date_arrivee = models.DateTimeField(default=timezone.now)
    date_triage = models.DateTimeField(null=True, blank=True)
    date_prise_en_charge = models.DateTimeField(null=True, blank=True)
    date_sortie = models.DateTimeField(null=True, blank=True)

    triage = models.CharField(max_length=2, choices=TRIAGE)
    statut = models.CharField(max_length=20, choices=STATUT, default='Triage')
    mode_arrivee = models.CharField(max_length=20, choices=MODE_ARRIVEE, default='Autonome')

    motif_principal = models.CharField(max_length=255)
    description_clinique = models.TextField(blank=True)
    antecedents_urgence = models.TextField(blank=True)

    medecin_urgentiste = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='passages_pris_en_charge'
    )
    infirmier_triage = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='passages_triages'
    )

    # Constantes à l'arrivée
    tension_systolique = models.IntegerField(null=True, blank=True)
    tension_diastolique = models.IntegerField(null=True, blank=True)
    frequence_cardiaque = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    saturation_o2 = models.IntegerField(null=True, blank=True)
    glasgow = models.IntegerField(null=True, blank=True)  # Score de Glasgow 3-15

    # Orientation
    orientation = models.CharField(max_length=100, blank=True)
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='passage_urgences'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_arrivee']
        indexes = [
            models.Index(fields=['statut', '-date_arrivee']),
            models.Index(fields=['triage', 'statut']),
        ]

    def __str__(self):
        return f"URG-{self.pk} — {self.patient} ({self.triage})"

    @property
    def duree_attente_minutes(self):
        if self.date_prise_en_charge and self.date_arrivee:
            return int((self.date_prise_en_charge - self.date_arrivee).total_seconds() / 60)
        return None

    @property
    def duree_passage_minutes(self):
        fin = self.date_sortie or timezone.now()
        return int((fin - self.date_arrivee).total_seconds() / 60)


class ActeUrgence(models.Model):
    passage = models.ForeignKey(PassageUrgences, on_delete=models.CASCADE, related_name='actes')
    type_acte = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    realise_par = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT)
    date_heure = models.DateTimeField(auto_now_add=True)
    materiel_utilise = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-date_heure']
