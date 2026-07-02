from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0001_initial'),
        ('personnel', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='ConsentementPatient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_consentement', models.CharField(choices=[('soins','Consentement aux soins'),('donnees','Traitement des données personnelles'),('recherche','Participation à la recherche'),('partage','Partage avec tiers (assurance, etc.)'),('communication','Communications marketing')], max_length=30)),
                ('statut', models.CharField(choices=[('accordé','Accordé'),('refusé','Refusé'),('retiré','Retiré')], default='accordé', max_length=20)),
                ('date_consentement', models.DateTimeField(auto_now_add=True)),
                ('date_expiration', models.DateField(blank=True, null=True)),
                ('date_retrait', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('version_document', models.CharField(default='1.0', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consentements', to='patients.patient')),
                ('recueilli_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.personnel')),
            ],
            options={'ordering': ['-date_consentement']},
        ),
        migrations.CreateModel(
            name='DemandeAccesDonnees',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_demande', models.CharField(choices=[('acces','Droit d\'accès'),('rectification','Droit de rectification'),('effacement','Droit à l\'effacement'),('portabilite','Droit à la portabilité'),('opposition','Droit d\'opposition')], max_length=20)),
                ('statut', models.CharField(choices=[('En attente','En attente'),('En cours','En cours'),('Traitée','Traitée'),('Refusée','Refusée')], default='En attente', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_traitement', models.DateTimeField(blank=True, null=True)),
                ('reponse', models.TextField(blank=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='demandes_rgpd', to='patients.patient')),
                ('traite_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.personnel')),
            ],
            options={'ordering': ['-date_demande']},
        ),
        migrations.AlterUniqueTogether(name='consentementpatient', unique_together={('patient', 'type_consentement', 'version_document')}),
    ]
