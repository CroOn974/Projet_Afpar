# Generated by Django 4.1.3 on 2022-12-05 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Datevente',
        ),
        migrations.DeleteModel(
            name='Detail',
        ),
        migrations.DeleteModel(
            name='Facture',
        ),
        migrations.DeleteModel(
            name='Histopays',
        ),
        migrations.DeleteModel(
            name='Histoproduit',
        ),
        migrations.DeleteModel(
            name='Pays',
        ),
        migrations.DeleteModel(
            name='Produit',
        ),
    ]
