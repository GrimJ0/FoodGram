# Generated by Django 3.2.9 on 2021-12-02 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_recipe_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit_measurement',
            new_name='dimension',
        ),
    ]