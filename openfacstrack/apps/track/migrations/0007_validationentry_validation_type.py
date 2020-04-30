# Generated by Django 3.0.5 on 2020-04-29 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0006_validationentry_entry_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationentry',
            name='validation_type',
            field=models.CharField(choices=[('SYNTAX', 'SYNTAX'), ('MODEL', 'MODEL')], default='SYNTAX', max_length=12),
        ),
    ]
