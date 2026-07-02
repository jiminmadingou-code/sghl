from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='BackupLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date_backup', models.DateTimeField(auto_now_add=True)),
                ('statut', models.CharField(choices=[('success','Succès'),('failed','Échec'),('running','En cours')], default='running', max_length=20)),
                ('taille_octets', models.BigIntegerField(default=0)),
                ('chemin_fichier', models.CharField(blank=True, max_length=500)),
                ('message', models.TextField(blank=True)),
                ('duree_secondes', models.IntegerField(default=0)),
            ],
            options={'ordering': ['-date_backup']},
        ),
    ]
