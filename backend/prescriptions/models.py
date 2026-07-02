from django.db import models
from django.utils import timezone
from audit.models import AuditTrail


class Prescription(models.Model):
    """Ordonnance électronique liée à une consultation."""
    STATUT = [
        ('Brouillon', 'Brouillon'),
        ('Validée', 'Validée'),
        ('Dispensée', 'Dispensée'),
        ('Annulée', 'Annulée'),
    ]

    consultation = models.ForeignKey(
        'patients.Consultation', on_delete=models.PROTECT, related_name='prescriptions'
    )
    medecin = models.ForeignKey(
        'personnel.Personnel', on_delete=models.PROTECT, related_name='prescriptions_emises'
    )
    patient = models.ForeignKey(
        'patients.Patient', on_delete=models.PROTECT, related_name='prescriptions'
    )
    date_prescription = models.DateTimeField(auto_now_add=True)
    date_validite = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT, default='Brouillon')
    notes = models.TextField(blank=True)

    # Immuabilité après validation
    verrouille = models.BooleanField(default=False)
    date_verrouillage = models.DateTimeField(null=True, blank=True)

    # Signature électronique
    signe_par = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='prescriptions_signees'
    )
    signature_hash = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_prescription']
        indexes = [
            models.Index(fields=['patient', '-date_prescription']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"Prescription #{self.id} - {self.patient} ({self.statut})"

    def valider(self, medecin):
        """Valider et verrouiller la prescription — immuable après."""
        if self.verrouille:
            raise ValueError("Prescription déjà verrouillée")
        import hashlib
        self.statut = 'Validée'
        self.verrouille = True
        self.date_verrouillage = timezone.now()
        self.signe_par = medecin
        # Hash de signature
        content = f"{self.id}{self.patient_id}{self.medecin_id}{self.date_prescription}"
        self.signature_hash = hashlib.sha256(content.encode()).hexdigest()
        self.save()
        AuditTrail.log(
            request=None, action_type='VALIDATE',
            model_name='Prescription', object_id=self.pk,
            details={'medecin_id': medecin.pk, 'patient_id': self.patient_id}
        )

    def save(self, *args, **kwargs):
        if self.pk and self.verrouille:
            # Empêcher toute modification d'une prescription verrouillée
            original = Prescription.objects.get(pk=self.pk)
            if original.verrouille:
                allowed = kwargs.pop('_force', False)
                if not allowed:
                    raise ValueError("Prescription verrouillée — immuable")
        super().save(*args, **kwargs)


class LignePrescription(models.Model):
    """Ligne de médicament dans une prescription."""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='lignes')
    medicament = models.ForeignKey('pharmacie.Medicament', on_delete=models.PROTECT)
    posologie = models.CharField(max_length=200)
    duree_jours = models.IntegerField(default=7)
    quantite = models.IntegerField(default=1)
    instructions = models.TextField(blank=True)
    dispensee = models.BooleanField(default=False)
    date_dispense = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.medicament.nom} - {self.posologie}"

    def dispenser(self, pharmacien):
        """Décrémenter le stock et marquer comme dispensé."""
        from pharmacie.models import LotMedicament, MouvementStock
        from django.db import transaction

        with transaction.atomic():
            # Trouver le lot disponible (FIFO — premier périmé en premier)
            lot = LotMedicament.objects.filter(
                medicament=self.medicament,
                quantite__gte=self.quantite
            ).order_by('date_peremption').first()

            if not lot:
                raise ValueError(f"Stock insuffisant pour {self.medicament.nom}")

            # Décrémenter le stock
            lot.quantite -= self.quantite
            lot.save()

            # Enregistrer le mouvement
            MouvementStock.objects.create(
                lot=lot,
                type_mouvement='Sortie',
                quantite=self.quantite,
                motif=f"Prescription #{self.prescription_id}",
                created_by=pharmacien
            )

            self.dispensee = True
            self.date_dispense = timezone.now()
            self.save()

            # Mettre à jour statut prescription si toutes les lignes dispensées
            if not self.prescription.lignes.filter(dispensee=False).exists():
                self.prescription.statut = 'Dispensée'
                self.prescription.save(_force=True)
