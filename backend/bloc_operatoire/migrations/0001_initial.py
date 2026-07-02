from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
        ('personnel', '0001_initial'),
        ('hospitalisations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalleOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('equipements', models.JSONField(blank=True, default=list)),
                ('actif', models.BooleanField(default=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hospitalisations.service')),
            ],
        ),
        migrations.CreateModel(
            name='InterventionChirurgicale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acte_principal', models.CharField(max_length=200)),
                ('code_ccam', models.CharField(blank=True, max_length=20)),
                ('actes_associes', models.JSONField(blank=True, default=list)),
                ('type_urgence', models.CharField(choices=[('Programmée', 'Programmée'), ('Urgente', 'Urgente'), ('Semi-urgente', 'Semi-urgente')], default='Programmée', max_length=20)),
                ('type_anesthesie', models.CharField(choices=[('Générale', 'Anesthésie générale'), ('Locorégionale', 'Anesthésie locorégionale'), ('Locale', 'Anesthésie locale'), ('Rachianesthésie', 'Rachianesthésie'), ('Péridurale', 'Péridurale')], max_length=20)),
                ('date_programmee', models.DateTimeField()),
                ('date_debut_reelle', models.DateTimeField(blank=True, null=True)),
                ('date_fin_reelle', models.DateTimeField(blank=True, null=True)),
                ('duree_prevue_minutes', models.IntegerField(default=60)),
                ('statut', models.CharField(choices=[('Programmée', 'Programmée'), ('En cours', 'En cours'), ('Terminée', 'Terminée'), ('Annulée', 'Annulée'), ('Reportée', 'Reportée')], default='Programmée', max_length=20)),
                ('compte_rendu_operatoire', models.TextField(blank=True)),
                ('complications', models.TextField(blank=True)),
                ('pertes_sanguines_ml', models.IntegerField(blank=True, null=True)),
                ('transfusions', models.JSONField(blank=True, default=list)),
                ('consignes_postop', models.TextField(blank=True)),
                ('destination_postop', models.CharField(blank=True, choices=[('SSPI', 'SSPI'), ('Réanimation', 'Réanimation'), ('Service', 'Service'), ('Domicile', 'Domicile')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='interventions_chirurgicales', to='patients.patient')),
                ('hospitalisation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='interventions_chirurgicales', to='hospitalisations.hospitalisation')),
                ('salle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='interventions', to='bloc_operatoire.salleoperation')),
                ('chirurgien_principal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='interventions_chirurgien', to='personnel.personnel')),
                ('chirurgien_aide', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interventions_aide', to='personnel.personnel')),
                ('anesthesiste', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='interventions_anesthesiste', to='personnel.personnel')),
                ('infirmier_bloc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interventions_infirmier', to='personnel.personnel')),
            ],
            options={'ordering': ['date_programmee']},
        ),
    ]
