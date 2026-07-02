import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturation', '0001_initial'),
        ('personnel', '0002_permission_alter_personnel_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EcritureComptable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_ecriture', models.CharField(choices=[('Encaissement', 'Encaissement'), ('Remboursement', 'Remboursement'), ('Ajustement', 'Ajustement'), ('Annulation', 'Annulation')], max_length=20)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=12)),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('facture', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ecritures', to='facturation.facture')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='personnel.personnel')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
