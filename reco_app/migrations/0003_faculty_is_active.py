# Generated by Django 5.0.7 on 2024-07-25 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reco_app', '0002_faculty_has_master_degree_alter_faculty_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
