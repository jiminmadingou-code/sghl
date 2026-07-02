from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gardes', '0002_alter_astreinte_id_alter_congesabsence_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='disponibilitemedecin',
            old_name='medicecin',
            new_name='medecin',
        ),
    ]
