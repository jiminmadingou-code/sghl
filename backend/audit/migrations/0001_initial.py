from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuditTrail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('user_email', models.CharField(blank=True, max_length=255, null=True)),
                ('action_type', models.CharField(choices=[('CREATE', 'CREATE'), ('UPDATE', 'UPDATE'), ('DELETE', 'DELETE'), ('VIEW', 'VIEW'), ('VALIDATE', 'VALIDATE'), ('EXPORT', 'EXPORT')], max_length=20)),
                ('model_name', models.CharField(max_length=100)),
                ('object_id', models.IntegerField()),
                ('old_value', models.JSONField(blank=True, default=dict)),
                ('new_value', models.JSONField(blank=True, default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('details', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'verbose_name': 'Audit Trail',
                'verbose_name_plural': 'Audit Trails',
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['-timestamp']), models.Index(fields=['model_name', 'object_id']), models.Index(fields=['user_id', '-timestamp'])],
            },
        ),
    ]
