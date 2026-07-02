"""Modèles pour la gestion hiérarchique des lits (Bâtiment > Service > Chambre > Lit)"""
from django.db import models
from django.core.validators import MinValueValidator


class Batiment(models.Model):
    """Bâtiment hospitalier."""
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=200)
    adresse = models.TextField(blank=True)
    nombre_etages = models.IntegerField(default=1)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Bâtiment'
        verbose_name_plural = 'Bâtiments'

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Service(models.Model):
    """Service médical/hospitalier."""
    TYPE_SERVICE = [
        ('Medecine', 'Médecine'),
        ('Chirurgie', 'Chirurgie'),
        ('Urgences', 'Urgences'),
        ('Reanimation', 'Réanimation'),
        ('Pedriatrie', 'Pédiatrie'),
        ('Gynécologie', 'Gynécologie'),
        ('Autre', 'Autre'),
    ]

    batiment = models.ForeignKey(Batiment, on_delete=models.CASCADE, related_name='services')
    code = models.CharField(max_length=20)
    nom = models.CharField(max_length=200)
    type_service = models.CharField(max_length=50, choices=TYPE_SERVICE)
    chef_service = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services_diriges'
    )
    telephone = models.CharField(max_length=20, blank=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        unique_together = ['batiment', 'code']

    def __str__(self):
        return f"{self.nom} ({self.batiment.nom})"

    @property
    def nombre_lits_total(self):
        return self.chambres.aggregate(total=models.Sum('nombre_lits'))['total'] or 0

    @property
    def nombre_lits_occupes(self):
        from hospitalisations.models import Hospitalisation
        return Hospitalisation.objects.filter(
            chambre__service=self,
            statut='Actif'
        ).count()

    @property
    def taux_occupation(self):
        total = self.nombre_lits_total
        if total == 0:
            return 0
        return (self.nombre_lits_occupes / total) * 100


class Chambre(models.Model):
    """Chambre d'hospitalisation."""
    TYPE_CHAMBRE = [
        ('Simple', 'Chambre Simple'),
        ('Double', 'Chambre Double'),
        ('Suite', 'Chambre de Suite'),
        ('Collective', 'Chambre Collective'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='chambres')
    numero = models.CharField(max_length=10)
    type_chambre = models.CharField(max_length=20, choices=TYPE_CHAMBRE)
    nombre_lits = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    equipements = models.JSONField(default=list, blank=True)
    tarif_nuitee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True
    )
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Chambre'
        verbose_name_plural = 'Chambres'
        unique_together = ['service', 'numero']

    def __str__(self):
        return f"{self.service.nom} - {self.numero} ({self.type_chambre})"

    @property
    def lits(self):
        return self.lits.all()

    @property
    def lits_occupes(self):
        return self.lits.filter(occupation__isnull=False, occupation__statut='Actif').count()

    @property
    def disponibilite(self):
        return self.nombre_lits - self.lits_occupes


class Lit(models.Model):
    """Lit d'hospitalisation - Unité de base d'admission."""
    statut = models.CharField(
        max_length=20,
        choices=[('Libre', 'Libre'), ('Occupe', 'Occupé'), ('Indisponible', 'Indisponible')],
        default='Libre'
    )
    numero_lit = models.CharField(max_length=10)
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='lits')
    equipements_specifiques = models.JSONField(default=list, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Lit'
        verbose_name_plural = 'Lits'
        unique_together = ['chambre', 'numero_lit']

    def __str__(self):
        return f"{self.chambre} - Lit {self.numero_lit}"

    def occuper(self, hospitalisation):
        """Occuper le lit par une hospitalisation."""
        self.statut = 'Occupe'
        self.occupation = hospitalisation
        self.save()

    def liberer(self):
        """Liberer le lit."""
        self.statut = 'Libre'
        self.occupation = None
        self.save()

    def rendre_indisponible(self):
        """Rendre le lit indisponible (maintenance, nettoyage, etc.)."""
        self.statut = 'Indisponible'
        self.save()

    @property
    def hospitalisation_courante(self):
        """Retourne l'hospitalisation courante si occupé."""
        if self.statut == 'Occupe':
            return getattr(self, 'occupation', None)
        return None


class TransferService(models.Model):
    """Historique des transferts inter-services."""
    hospitalisation = models.ForeignKey(
        'hospitalisations.Hospitalisation',
        on_delete=models.CASCADE,
        related_name='transfers'
    )
    service_origine = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='transfers_sortants'
    )
    service_destin = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='transfers_entrants'
    )
    date_transfer = models.DateTimeField(auto_now_add=True)
    motif = models.TextField(blank=True)
    realise_par = models.ForeignKey(
        'personnel.Personnel',
        on_delete=models.PROTECT,
        related_name='transfers_effectues'
    )

    class Meta:
        ordering = ['-date_transfer']

    def __str__(self):
        return f"Transfer: {self.service_origine} → {self.service_destin} ({self.date_transfer})"
