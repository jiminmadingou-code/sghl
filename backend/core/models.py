"""
Extension du model User avec champ téléphone.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """User avec champ téléphone."""
    phone = models.CharField(max_length=20, blank=True, default='')
    role = models.CharField(
        max_length=50,
        default='Patient',
        choices=[
            ('Patient', 'Patient'),
            ('Médecin', 'Médecin'),
            ('Infirmier', 'Infirmier'),
            ('Biologiste', 'Biologiste'),
            ('Pharmacien', 'Pharmacien'),
            ('Caissier', 'Caissier'),
            ('Receptionniste', 'Réceptionniste'),
            ('Admin', 'Administrateur'),
        ]
    )
    is_patient = models.BooleanField(default=False)
    nss = models.CharField(max_length=20, blank=True, default='')  # Numéro de sécurité sociale

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
