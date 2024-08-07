# Generated by Django 5.0.7 on 2024-07-27 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupinfoth',
            name='members',
        ),
        migrations.AddField(
            model_name='groupinfoth',
            name='member1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='groupinfoth',
            name='member2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='groupinfoth',
            name='member3',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
