# Generated by Django 4.2.11 on 2024-04-12 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_buildingmaterials_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.buildingmaterials')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
            ],
            options={
                'unique_together': {('user', 'material')},
            },
        ),
    ]
