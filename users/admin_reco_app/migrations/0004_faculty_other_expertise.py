# Generated by Django 5.0.7 on 2024-08-04 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_reco_app', '0003_remove_faculty_other_expertise_faculty_expertise_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='other_expertise',
            field=models.TextField(blank=True, null=True),
        ),
    ]
