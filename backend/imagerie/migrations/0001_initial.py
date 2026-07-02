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
            name='Modalite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('actif', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExamenImagerie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_anatomique', models.CharField(max_length=100)),
                ('indication_clinique', models.TextField()),
                ('urgence', models.CharField(choices=[('Normal', 'Normal'), ('Urgent', 'Urgent'), ('STAT', 'STAT — Immédiat')], default='Normal', max_length=10)),
                ('statut', models.CharField(choices=[('Prescrit', 'Prescrit'), ('Planifié', 'Planifié'), ('En cours', 'En cours'), ('Réalisé', 'Réalisé'), ('Interprété', 'Interprété'), ('Validé', 'Validé'), ('Annulé', 'Annulé')], default='Prescrit', max_length=20)),
                ('date_prescription', models.DateTimeField(auto_now_add=True)),
                ('date_realisation', models.DateTimeField(blank=True, null=True)),
                ('date_interpretation', models.DateTimeField(blank=True, null=True)),
                ('compte_rendu', models.TextField(blank=True)),
                ('conclusion', models.TextField(blank=True)),
                ('rapport_pdf', models.FileField(blank=True, null=True, upload_to='imagerie/rapports/')),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('verrouille', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hospitalisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='examens_imagerie', to='hospitalisations.hospitalisation')),
                ('modalite', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='imagerie.modalite')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='examens_imagerie', to='patients.patient')),
                ('prescripteur', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='imageries_prescrites', to='personnel.personnel')),
                ('radiologue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='imageries_interpretees', to='personnel.personnel')),
                ('valide_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='imageries_validees', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_prescription']},
        ),
        migrations.CreateModel(
            name='ImageDICOM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='imagerie/dicom/')),
                ('serie', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('taille_octets', models.BigIntegerField(default=0)),
                ('mime_type', models.CharField(default='application/dicom', max_length=100)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='imagerie.examenimagerie')),
            ],
            options={'ordering': ['uploaded_at']},
        ),
    ]
