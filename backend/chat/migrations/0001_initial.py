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
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('sujet', models.CharField(blank=True, max_length=200)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_dernier_message', models.DateTimeField(auto_now=True)),
                ('statut', models.CharField(choices=[('ouverte','Ouverte'),('fermee','Fermée'),('archivée','Archivée')], default='ouverte', max_length=20)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='patients.patient')),
                ('medicecin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations_medecin', to='personnel.personnel')),
                ('hospitalisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversations', to='hospitalisations.hospitalisation')),
            ],
            options={'ordering': ['-date_dernier_message']},
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('contenu', models.TextField()),
                ('date_envoi', models.DateTimeField(auto_now_add=True)),
                ('lu', models.BooleanField(default=False)),
                ('date_lecture', models.DateTimeField(blank=True, null=True)),
                ('piece_jointe', models.FileField(blank=True, null=True, upload_to='chat_attachments/')),
                ('type_piece_jointe', models.CharField(blank=True, max_length=50)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.conversation')),
                ('expediteur', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages_envoyes', to='personnel.personnel')),
                ('destinataire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='messages_recus', to='personnel.personnel')),
            ],
            options={'ordering': ['date_envoi']},
        ),
        migrations.CreateModel(
            name='NotificationPush',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_notification', models.CharField(choices=[('message','Nouveau Message'),('rendez_vous','Rappel Rendez-vous'),('ordonnance','Nouvelle Ordonnance'),('resultat','Résultat Disponible'),('soin','Rappel de Soin'),('general','Notification Générale')], max_length=50)),
                ('titre', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('lue', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_expiration', models.DateTimeField(blank=True, null=True)),
                ('data_contexte', models.JSONField(blank=True, default=dict)),
                ('device_token', models.CharField(blank=True, max_length=500)),
                ('envoye', models.BooleanField(default=False)),
                ('date_envoi', models.DateTimeField(blank=True, null=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications_push', to='personnel.personnel')),
            ],
            options={'ordering': ['-date_creation']},
        ),
    ]
