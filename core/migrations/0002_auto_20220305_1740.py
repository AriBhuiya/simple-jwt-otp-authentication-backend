# Generated by Django 3.0.7 on 2022-03-05 17:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonverifieduser',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
