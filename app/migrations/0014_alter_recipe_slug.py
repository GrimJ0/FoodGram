# Generated by Django 3.2.9 on 2021-12-21 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20211218_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='slug',
            field=models.SlugField(max_length=255, unique=True, verbose_name='slug'),
        ),
    ]
