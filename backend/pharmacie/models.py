from django.db import models

class Medicament(models.Model):
    nom = models.CharField(max_length=200)
    categorie = models.CharField(max_length=100)
    unite = models.CharField(max_length=20, default='comprimé')
    seuil_alerte = models.PositiveIntegerField(default=50)

    def __str__(self): return self.nom

class LotMedicament(models.Model):
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE, related_name='lots')
    numero_lot = models.CharField(max_length=50)
    quantite = models.PositiveIntegerField(default=0)
    date_peremption = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def statut(self):
        from django.utils import timezone
        import datetime
        if self.quantite == 0:
            return 'Rupture'
        if self.quantite <= self.medicament.seuil_alerte:
            return 'Alerte'
        if self.date_peremption <= (timezone.now().date() + datetime.timedelta(days=90)):
            return 'Alerte'
        return 'Normal'

class MouvementStock(models.Model):
    TYPE = [('Entrée', 'Entrée'), ('Sortie', 'Sortie'), ('Ajustement', 'Ajustement')]
    lot = models.ForeignKey(LotMedicament, on_delete=models.PROTECT)
    type_mouvement = models.CharField(max_length=20, choices=TYPE)
    quantite = models.IntegerField()
    motif = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
