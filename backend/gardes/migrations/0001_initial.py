from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('personnel', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='TypeGarde',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('duree_heures', models.IntegerField(default=12)),
                ('coefficient_paiement', models.DecimalField(decimal_places=2, default=1.0, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='PlanningGarde',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_debut', models.DateTimeField()),
                ('date_fin', models.DateTimeField()),
                ('statut', models.CharField(choices=[('planifie','Planifié'),('confirmé','Confirmé'),('annule','Annulé'),('remplace','Remplacé')], default='planifie', max_length=20)),
                ('lieu', models.CharField(blank=True, max_length=200)),
                ('observations', models.TextField(blank=True)),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plannings_garde', to='personnel.personnel')),
                ('type_garde', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gardes.typegarde')),
                ('valide_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gardes_validees', to='personnel.personnel')),
                ('remplace_planning', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='remplacements_recus', to='gardes.planninggarde')),
                ('remplace_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='remplacements_effectues', to='gardes.planninggarde')),
            ],
            options={'ordering': ['date_debut']},
        ),
        migrations.CreateModel(
            name='Astreinte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_debut', models.DateTimeField()),
                ('date_fin', models.DateTimeField()),
                ('type_contact', models.CharField(choices=[('telephonique','Téléphonique'),('physique','Sur place')], max_length=20)),
                ('actif', models.BooleanField(default=True)),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='astreintes', to='personnel.personnel')),
            ],
            options={'ordering': ['date_debut']},
        ),
        migrations.CreateModel(
            name='DisponibiliteMedecin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('heure_debut', models.TimeField()),
                ('heure_fin', models.TimeField()),
                ('duree_consultation_minutes', models.IntegerField(default=30)),
                ('creneaux_disponibles', models.IntegerField(default=0)),
                ('exceptionnelle', models.BooleanField(default=False)),
                ('motif_exception', models.CharField(blank=True, max_length=200)),
                ('medicecin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disponibilites', to='personnel.personnel')),
            ],
            options={'ordering': ['date', 'heure_debut']},
        ),
        migrations.CreateModel(
            name='CongesAbsence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_absence', models.CharField(choices=[('conge_paye','Congés Payés'),('maladie','Maladie'),('congematernal','Congé Maternité'),('congeparental','Congé Parental'),('autorisation','Autorisation d\'Absence'),('autre','Autre')], max_length=50)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField()),
                ('statut', models.CharField(choices=[('demande','Demandé'),('accepte','Accepté'),('refuse','Refusé')], default='demande', max_length=20)),
                ('motif', models.TextField(blank=True)),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='absences', to='personnel.personnel')),
                ('valide_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='absences_validees', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_debut']},
        ),
        migrations.AlterUniqueTogether(name='disponibilitemedecin', unique_together={('medicecin', 'date', 'heure_debut')}),
    ]
