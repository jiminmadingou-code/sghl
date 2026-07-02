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
            name='ArchiveDossier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statut', models.CharField(choices=[('Actif', 'Actif'), ('Archivé', 'Archivé'), ('Anonymisé', 'Anonymisé'), ('Détruit', 'Détruit')], default='Actif', max_length=20)),
                ('date_archivage', models.DateTimeField(blank=True, null=True)),
                ('date_destruction_prevue', models.DateField(blank=True, null=True)),
                ('motif_archivage', models.TextField(blank=True)),
                ('consentement_donne', models.BooleanField(default=False)),
                ('date_consentement', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='archive', to='patients.patient')),
                ('archive_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='personnel.personnel')),
            ],
            options={'ordering': ['-date_archivage']},
        ),
        migrations.CreateModel(
            name='DocumentMedical',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_document', models.CharField(choices=[('Compte-rendu', 'Compte-rendu'), ('Ordonnance', 'Ordonnance'), ('Résultat labo', 'Résultat laboratoire'), ('Imagerie', 'Imagerie'), ('Consentement', 'Consentement'), ('Courrier', 'Courrier médical'), ('Autre', 'Autre')], max_length=30)),
                ('titre', models.CharField(max_length=255)),
                ('fichier', models.FileField(upload_to='documents/%Y/%m/')),
                ('mime_type', models.CharField(max_length=100)),
                ('taille_octets', models.BigIntegerField(default=0)),
                ('version', models.IntegerField(default=1)),
                ('hash_sha256', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('acces_patient', models.BooleanField(default=True)),
                ('confidentiel', models.BooleanField(default=False)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documents', to='patients.patient')),
                ('cree_par', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='personnel.personnel')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AccesDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_acces', models.DateTimeField(auto_now_add=True)),
                ('type_acces', models.CharField(choices=[('Lecture', 'Lecture'), ('Téléchargement', 'Téléchargement'), ('Impression', 'Impression')], max_length=20)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='acces', to='archivage.documentmedical')),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='personnel.personnel')),
            ],
            options={'ordering': ['-date_acces']},
        ),
    ]
