# Generated by Django 5.0.7 on 2024-08-03 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_firstname_customuser_lastname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_admin',
        ),
    ]
