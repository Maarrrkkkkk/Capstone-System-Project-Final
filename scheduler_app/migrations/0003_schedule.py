# Generated by Django 5.0.7 on 2024-07-27 04:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reco_app', '0006_faculty_is_active'),
        ('scheduler_app', '0002_remove_groupinfoth_members_groupinfoth_member1_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.CharField(max_length=20)),
                ('date', models.DateField()),
                ('faculty1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculty1', to='reco_app.faculty')),
                ('faculty2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculty2', to='reco_app.faculty')),
                ('faculty3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculty3', to='reco_app.faculty')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler_app.groupinfoth')),
            ],
        ),
    ]
