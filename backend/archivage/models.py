from django.db import models
from django.utils import timezone


class ArchiveDossier(models.Model):
    """Archivage longue durée des dossiers médicaux."""
    STATUT = [
        ('Actif', 'Actif'),
        ('Archivé', 'Archivé'),
        ('Anonymisé', 'Anonymisé'),
        ('Détruit', 'Détruit'),
    ]
    DUREE_CONSERVATION = 20  # Années (norme française)

    patient = models.OneToOneField('patients.Patient', on_delete=models.PROTECT, related_name='archive')
    statut = models.CharField(max_length=20, choices=STATUT, default='Actif')
    date_archivage = models.DateTimeField(null=True, blank=True)
    date_destruction_prevue = models.DateField(null=True, blank=True)
    archive_par = models.ForeignKey(
        'personnel.Personnel', on_delete=models.SET_NULL, null=True, blank=True
    )
    motif_archivage = models.TextField(blank=True)
    consentement_donne = models.BooleanField(default=False)
    date_consentement = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_archivage']

    def archiver(self, personnel, motif=''):
        from datetime import timedelta
        self.statut = 'Archivé'
        self.date_archivage = timezone.now()
        self.archive_par = personnel
        self.motif_archivage = motif
        self.date_destruction_prevue = (
            timezone.now() + timedelta(days=365 * self.DUREE_CONSERVATION)
        ).date()
        self.save()


class DocumentMedical(models.Model):
    """Documents médicaux archivés avec versioning."""
    TYPE_DOC = [
        ('Compte-rendu', 'Compte-rendu'),
        ('Ordonnance', 'Ordonnance'),
        ('Résultat labo', 'Résultat laboratoire'),
        ('Imagerie', 'Imagerie'),
        ('Consentement', 'Consentement'),
        ('Courrier', 'Courrier médical'),
        ('Autre', 'Autre'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='documents')
    type_document = models.CharField(max_length=30, choices=TYPE_DOC)
    titre = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    mime_type = models.CharField(max_length=100)
    taille_octets = models.BigIntegerField(default=0)
    version = models.IntegerField(default=1)
    hash_sha256 = models.CharField(max_length=64, blank=True)

    cree_par = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Accès
    acces_patient = models.BooleanField(default=True)
    confidentiel = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'type_document', '-created_at']),
        ]

    def __str__(self):
        return f"{self.type_document} — {self.titre} (v{self.version})"

    def calculer_hash(self):
        import hashlib
        if self.fichier:
            sha256 = hashlib.sha256()
            for chunk in self.fichier.chunks():
                sha256.update(chunk)
            self.hash_sha256 = sha256.hexdigest()
            self.save(update_fields=['hash_sha256'])


class AccesDocument(models.Model):
    """Traçabilité des accès aux documents sensibles."""
    document = models.ForeignKey(DocumentMedical, on_delete=models.CASCADE, related_name='acces')
    personnel = models.ForeignKey('personnel.Personnel', on_delete=models.PROTECT)
    date_acces = models.DateTimeField(auto_now_add=True)
    type_acces = models.CharField(
        max_length=20,
        choices=[('Lecture', 'Lecture'), ('Téléchargement', 'Téléchargement'), ('Impression', 'Impression')]
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-date_acces']
