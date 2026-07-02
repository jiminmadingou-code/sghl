"""
Modèles pour le suivi des backups
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class BackupJob(models.Model):
    """Configuration des jobs de backup"""
    TYPE = [
        ('database', 'Base de données'),
        ('media', 'Fichiers médias'),
        ('full', 'Backup complet'),
    ]
    
    STATUS = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
    ]
    
    name = models.CharField(max_length=100)
    backup_type = models.CharField(max_length=20, choices=TYPE)
    schedule = models.CharField(max_length=50, help_text="Cron expression")
    is_active = models.BooleanField(default=True)
    retention_days = models.PositiveIntegerField(default=30)
    destination = models.CharField(max_length=255, help_text="S3 bucket ou chemin local")
    encrypted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Job de Backup"
        verbose_name_plural = "Jobs de Backup"
    
    def __str__(self):
        return f"{self.name} ({self.backup_type})"


class BackupExecution(models.Model):
    """Historique des exécutions de backup"""
    STATUS = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
    ]
    
    job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, help_text="Taille en octets")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    duration_seconds = models.PositiveIntegerField(null=True)
    error_message = models.TextField(blank=True)
    checksum = models.CharField(max_length=64, blank=True, help_text="SHA256")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = "Exécution de Backup"
        verbose_name_plural = "Exécutions de Backup"
    
    def __str__(self):
        return f"{self.job.name} - {self.status} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration(self):
        if self.duration_seconds:
            return f"{self.duration_seconds}s"
        return "En cours"
    
    def is_old(self, days=30):
        """Vérifier si le backup est plus vieux que X jours"""
        threshold = timezone.now() - timedelta(days=days)
        return self.start_time < threshold


class RestoreTest(models.Model):
    """Historique des tests de restauration (DRP)"""
    STATUS = [
        ('pending', 'En attente'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
    ]
    
    backup = models.ForeignKey(BackupExecution, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    test_database = models.CharField(max_length=100, help_text="Nom de la DB de test")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    duration_seconds = models.PositiveIntegerField(null=True)
    error_message = models.TextField(blank=True)
    verified_by = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Test de Restauration"
        verbose_name_plural = "Tests de Restauration"
    
    def __str__(self):
        return f"Test restauration {self.backup.job.name} - {self.status}"
