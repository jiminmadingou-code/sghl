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
            name='PassageUrgences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_arrivee', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_triage', models.DateTimeField(blank=True, null=True)),
                ('date_prise_en_charge', models.DateTimeField(blank=True, null=True)),
                ('date_sortie', models.DateTimeField(blank=True, null=True)),
                ('triage', models.CharField(choices=[('P1', 'P1 — Urgence absolue (rouge)'), ('P2', 'P2 — Urgence relative (orange)'), ('P3', 'P3 — Urgence différée (jaune)'), ('P4', 'P4 — Non urgent (vert)'), ('P5', 'P5 — Décédé (noir)')], max_length=2)),
                ('statut', models.CharField(choices=[('Triage', 'Triage'), ('En attente', 'En attente'), ('En cours', 'En cours'), ('Hospitalisé', 'Hospitalisé'), ('Sorti', 'Sorti'), ('Transféré', 'Transféré'), ('Décédé', 'Décédé')], default='Triage', max_length=20)),
                ('mode_arrivee', models.CharField(choices=[('Ambulance', 'Ambulance'), ('SMUR', 'SMUR'), ('Pompiers', 'Pompiers'), ('Autonome', 'Autonome'), ('Hélicoptère', 'Hélicoptère')], default='Autonome', max_length=20)),
                ('motif_principal', models.CharField(max_length=255)),
                ('description_clinique', models.TextField(blank=True)),
                ('antecedents_urgence', models.TextField(blank=True)),
                ('tension_systolique', models.IntegerField(blank=True, null=True)),
                ('tension_diastolique', models.IntegerField(blank=True, null=True)),
                ('frequence_cardiaque', models.IntegerField(blank=True, null=True)),
                ('temperature', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('saturation_o2', models.IntegerField(blank=True, null=True)),
                ('glasgow', models.IntegerField(blank=True, null=True)),
                ('orientation', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='passages_urgences', to='patients.patient')),
                ('medecin_urgentiste', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='passages_pris_en_charge', to='personnel.personnel')),
                ('infirmier_triage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='passages_triages', to='personnel.personnel')),
                ('hospitalisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='passage_urgences', to='hospitalisations.hospitalisation')),
            ],
            options={'ordering': ['-date_arrivee']},
        ),
        migrations.CreateModel(
            name='ActeUrgence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_acte', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('date_heure', models.DateTimeField(auto_now_add=True)),
                ('materiel_utilise', models.JSONField(blank=True, default=list)),
                ('passage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actes', to='urgences.passageurgences')),
                ('realise_par', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='personnel.personnel')),
            ],
            options={'ordering': ['-date_heure']},
        ),
        migrations.AddIndex(
            model_name='passageurgences',
            index=models.Index(fields=['statut', '-date_arrivee'], name='urgences_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='passageurgences',
            index=models.Index(fields=['triage', 'statut'], name='urgences_triage_idx'),
        ),
    ]
