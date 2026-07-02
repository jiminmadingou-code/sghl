from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0001_initial'),
        ('personnel', '0001_initial'),
        ('pharmacie', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_prescription', models.DateTimeField(auto_now_add=True)),
                ('date_validite', models.DateField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('Brouillon','Brouillon'),('Validée','Validée'),('Dispensée','Dispensée'),('Annulée','Annulée')], default='Brouillon', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('verrouille', models.BooleanField(default=False)),
                ('date_verrouillage', models.DateTimeField(blank=True, null=True)),
                ('signature_hash', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prescriptions', to='patients.consultation')),
                ('medecin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prescriptions_emises', to='personnel.personnel')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prescriptions', to='patients.patient')),
                ('signe_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescriptions_signees', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_prescription']},
        ),
        migrations.CreateModel(
            name='LignePrescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('posologie', models.CharField(max_length=200)),
                ('duree_jours', models.IntegerField(default=7)),
                ('quantite', models.IntegerField(default=1)),
                ('instructions', models.TextField(blank=True)),
                ('dispensee', models.BooleanField(default=False)),
                ('date_dispense', models.DateTimeField(blank=True, null=True)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='prescriptions.prescription')),
                ('medicament', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pharmacie.medicament')),
            ],
        ),
    ]
