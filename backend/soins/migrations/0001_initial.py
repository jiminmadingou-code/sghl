from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0001_initial'),
        ('personnel', '0001_initial'),
        ('hospitalisations', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='TypeSoin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('nom', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('duree_estimee_minutes', models.IntegerField(default=15)),
                ('categorie', models.CharField(blank=True, max_length=100)),
                ('actif', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanificationSoins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_heure_prevue', models.DateTimeField()),
                ('duree_prevue_minutes', models.IntegerField(default=15)),
                ('statut', models.CharField(choices=[('Planifié','Planifié'),('En cours','En cours'),('Terminé','Terminé'),('Annulé','Annulé'),('Omis','Omis')], default='Planifié', max_length=20)),
                ('priorite', models.CharField(choices=[('Normale','Normale'),('Urgente','Urgente'),('Haute','Haute')], default='Normale', max_length=10)),
                ('instructions', models.TextField(blank=True)),
                ('date_heure_reelle', models.DateTimeField(blank=True, null=True)),
                ('notes_realisation', models.TextField(blank=True)),
                ('alerte_omission', models.BooleanField(default=False)),
                ('date_dernier_rappel', models.DateTimeField(blank=True, null=True)),
                ('hospitalisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soins_planifies', to='hospitalisations.hospitalisation')),
                ('type_soin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='soins.typesoin')),
                ('infirmier_assigne', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='soins_a_realiser', to='personnel.personnel')),
                ('realise_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='soins_realises', to='personnel.personnel')),
            ],
            options={'ordering': ['date_heure_prevue']},
        ),
        migrations.CreateModel(
            name='ConstanteVitale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_constante', models.CharField(choices=[('Temperature','Température (°C)'),('Pouls','Pouls (bpm)'),('PressionSystolique','Pression Artérielle Systolique (mmHg)'),('PressionDiastolique','Pression Artérielle Diastolique (mmHg)'),('Respiration','Fréquence Respiratoire (min⁻¹)'),('SaturationO2','Saturation en O2 (%)'),('Glycemie','Glycémie (mg/dL)'),('Poids','Poids (kg)'),('Taille','Taille (cm)'),('IMC','Indice de Masse Corporelle')], max_length=50)),
                ('valeur', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unite', models.CharField(blank=True, max_length=20)),
                ('date_mesure', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('alerte_seuil', models.BooleanField(default=False)),
                ('seuil_bas', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('seuil_haut', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('hospitalisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constantsvitales', to='hospitalisations.hospitalisation')),
                ('mesure_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='constantes_mesurees', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_mesure']},
        ),
        migrations.CreateModel(
            name='InterventionInfirmiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_heure', models.DateTimeField(auto_now_add=True)),
                ('type_intervention', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('medicaments_administres', models.JSONField(blank=True, default=list)),
                ('reponse_patient', models.TextField(blank=True)),
                ('hospitalisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interventions', to='hospitalisations.hospitalisation')),
                ('infirmier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='interventions', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_heure']},
        ),
    ]
