from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
        ('personnel', '0001_initial'),
        ('rendez_vous', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionTeleconsultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_heure_prevue', models.DateTimeField()),
                ('date_debut_reelle', models.DateTimeField(blank=True, null=True)),
                ('date_fin_reelle', models.DateTimeField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('Planifiée', 'Planifiée'), ('En attente', 'En attente'), ('En cours', 'En cours'), ('Terminée', 'Terminée'), ('Annulée', 'Annulée'), ('Absent', 'Patient absent')], default='Planifiée', max_length=20)),
                ('motif', models.CharField(max_length=255)),
                ('lien_patient', models.CharField(blank=True, max_length=255)),
                ('lien_medecin', models.CharField(blank=True, max_length=255)),
                ('token_session', models.CharField(blank=True, max_length=64, unique=True)),
                ('notes_consultation', models.TextField(blank=True)),
                ('diagnostic', models.CharField(blank=True, max_length=255)),
                ('prescription_generee', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teleconsultations', to='patients.patient')),
                ('medecin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teleconsultations', to='personnel.personnel')),
                ('rendez_vous', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teleconsultation', to='rendez_vous.rendezvous')),
            ],
            options={'ordering': ['date_heure_prevue']},
        ),
    ]
