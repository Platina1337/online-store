# Generated by Django 4.2.11 on 2024-04-04 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
