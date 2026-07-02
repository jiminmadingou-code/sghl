from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0001_initial'),
        ('personnel', '0001_initial'),
        ('gardes', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='RendezVous',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_heure', models.DateTimeField()),
                ('duree_minutes', models.IntegerField(default=30)),
                ('type_rdv', models.CharField(choices=[('Consultation','Consultation'),('Suivi','Suivi'),('Urgence','Urgence'),('Téléconsultation','Téléconsultation')], default='Consultation', max_length=20)),
                ('motif', models.CharField(max_length=255)),
                ('statut', models.CharField(choices=[('En attente','En attente'),('Confirmé','Confirmé'),('Annulé','Annulé'),('Terminé','Terminé'),('Absent','Absent')], default='En attente', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('confirmation_envoyee', models.BooleanField(default=False)),
                ('rappel_envoye', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rendez_vous', to='patients.patient')),
                ('medecin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rendez_vous', to='personnel.personnel')),
                ('disponibilite', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rendez_vous', to='gardes.disponibilitemedecin')),
            ],
            options={'ordering': ['date_heure']},
        ),
        migrations.AddIndex(model_name='rendezvous', index=models.Index(fields=['medecin', 'date_heure'], name='rdv_medecin_idx')),
        migrations.AddIndex(model_name='rendezvous', index=models.Index(fields=['patient', '-date_heure'], name='rdv_patient_idx')),
        migrations.AddIndex(model_name='rendezvous', index=models.Index(fields=['statut'], name='rdv_statut_idx')),
    ]
