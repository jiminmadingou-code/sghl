from django.db import migrations


def remove_mamadou_diallo(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    # Supprimer uniquement les patients de démo sans compte utilisateur lié
    Patient.objects.filter(nom='Diallo', prenom='Mamadou', user__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('patients', '0003_patient_user'),
    ]

    operations = [
        migrations.RunPython(remove_mamadou_diallo, migrations.RunPython.noop),
    ]
