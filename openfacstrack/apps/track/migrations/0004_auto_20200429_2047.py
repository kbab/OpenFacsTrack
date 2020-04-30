# Generated by Django 3.0.5 on 2020-04-29 20:47

from django.db import migrations, models
import django.db.models.deletion
import openfacstrack.apps.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0003_auto_20200429_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfile',
            name='valid_model',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='valid_syntax',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ValidationEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', openfacstrack.apps.core.models.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', openfacstrack.apps.core.models.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('key', models.CharField(max_length=240)),
                ('value', models.TextField()),
                ('subject_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='track.UploadedFile')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
