# Generated by Django 5.2.1 on 2025-05-30 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0002_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RoleAssignment',
        ),
    ]
