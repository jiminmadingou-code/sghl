from django.db import models
from audit.models import AuditTrail

WORKFLOW = [
    ('Commande', 'Commande'),
    ('Prélèvement', 'Prélèvement'),
    ('Affectation', 'Affectation'),
    ('Saisie résultats', 'Saisie résultats'),
    ('Validé', 'Validé'),
    ('Publié', 'Publié'),
]


class ExamenLaboratoire(models.Model):
    PRIORITE = [('Normal', 'Normal'), ('Urgent', 'Urgent')]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='examens')
    prescripteur = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, related_name='examens_prescrits')
    technicien = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, null=True, blank=True, related_name='examens_traites')
    type_examen = models.CharField(max_length=100)
    priorite = models.CharField(max_length=10, choices=PRIORITE, default='Normal')
    statut = models.CharField(max_length=20, choices=WORKFLOW, default='Commande')
    resultat = models.TextField(blank=True)
    valide_par = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT, null=True, blank=True, related_name='examens_valides')
    date_prescription = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    resultat_immutable = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_prescription']

    def save(self, *args, **kwargs):
        """Audit trail obligatoire sur modification avant validation."""
        if self.pk and not self.resultat_immutable:
            try:
                old = ExamenLaboratoire.objects.get(pk=self.pk)
                if old.statut != self.statut or old.resultat != self.resultat:
                    AuditTrail.log(
                        request=None,
                        action_type='UPDATE',
                        model_name='ExamenLaboratoire',
                        object_id=self.pk,
                        old_value={'statut': old.statut, 'resultat': old.resultat},
                        new_value={'statut': self.statut, 'resultat': self.resultat},
                    )
            except ExamenLaboratoire.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def valider(self, biologiste):
        """Validation exclusive par biologiste — résultat devient immuable."""
        from django.utils import timezone
        self.statut = 'Validé'
        self.valide_par = biologiste
        self.date_validation = timezone.now()
        self.resultat_immutable = True
        self.save()
        AuditTrail.log(
            request=None,
            action_type='VALIDATE',
            model_name='ExamenLaboratoire',
            object_id=self.pk,
            details={'biologiste_id': biologiste.pk, 'patient_id': self.patient_id},
        )
