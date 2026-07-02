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
            name='Grossesse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut_grossesse', models.DateField()),
                ('date_terme_prevue', models.DateField()),
                ('type_grossesse', models.CharField(choices=[('Simple', 'Simple'), ('Gémellaire', 'Gémellaire'), ('Triple', 'Triple')], default='Simple', max_length=20)),
                ('statut', models.CharField(choices=[('En cours', 'En cours'), ('Accouchée', 'Accouchée'), ('Fausse couche', 'Fausse couche'), ('Interruption', 'Interruption')], default='En cours', max_length=20)),
                ('groupe_sanguin_confirme', models.CharField(blank=True, max_length=3)),
                ('rhesus', models.CharField(blank=True, max_length=5)),
                ('antecedents_obstetricaux', models.TextField(blank=True)),
                ('facteurs_risque', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patiente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='grossesses', to='patients.patient')),
                ('medecin_referent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='grossesses_suivies', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_debut_grossesse']},
        ),
        migrations.CreateModel(
            name='ConsultationPrenatale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_consultation', models.IntegerField()),
                ('date', models.DateTimeField()),
                ('poids_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('tension_systolique', models.IntegerField(blank=True, null=True)),
                ('tension_diastolique', models.IntegerField(blank=True, null=True)),
                ('hauteur_uterine_cm', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('bcf', models.IntegerField(blank=True, null=True)),
                ('presentation', models.CharField(blank=True, max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('examens_prescrits', models.JSONField(blank=True, default=list)),
                ('grossesse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations_prenatales', to='maternite.grossesse')),
                ('medecin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='personnel.personnel')),
            ],
            options={'ordering': ['numero_consultation']},
        ),
        migrations.CreateModel(
            name='Accouchement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_heure', models.DateTimeField()),
                ('type_accouchement', models.CharField(choices=[('Voie basse', 'Voie basse spontanée'), ('Forceps', 'Forceps'), ('Ventouse', 'Ventouse'), ('Césarienne', 'Césarienne programmée'), ('Césarienne urgente', 'Césarienne urgente')], max_length=30)),
                ('duree_travail_heures', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('complications', models.TextField(blank=True)),
                ('pertes_sanguines_ml', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('grossesse', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='accouchement', to='maternite.grossesse')),
                ('sage_femme', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='accouchements_sf', to='personnel.personnel')),
                ('medecin_present', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accouchements_med', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_heure']},
        ),
        migrations.CreateModel(
            name='Nouveau_Ne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sexe', models.CharField(choices=[('M', 'Masculin'), ('F', 'Féminin'), ('I', 'Indéterminé')], max_length=1)),
                ('poids_naissance_g', models.IntegerField()),
                ('taille_cm', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('perimetre_cranien_cm', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('score_apgar_1min', models.IntegerField(blank=True, null=True)),
                ('score_apgar_5min', models.IntegerField(blank=True, null=True)),
                ('statut_vital', models.CharField(choices=[('Vivant', 'Vivant'), ('Mort-né', 'Mort-né'), ('Décédé', 'Décédé')], default='Vivant', max_length=10)),
                ('anomalies_congenitales', models.TextField(blank=True)),
                ('accouchement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nouveau_nes', to='maternite.accouchement')),
                ('patient_cree', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='naissance', to='patients.patient')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='consultationprenatale',
            unique_together={('grossesse', 'numero_consultation')},
        ),
    ]
