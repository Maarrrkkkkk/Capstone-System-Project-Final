# Generated by Django 5.0.7 on 2024-08-03 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='firstname',
            field=models.CharField(default='First', max_length=30),
        ),
        migrations.AddField(
            model_name='customuser',
            name='lastname',
            field=models.CharField(default='Last', max_length=30),
        ),
    ]
