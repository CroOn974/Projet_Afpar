# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Annee(models.Model):
    anneevente = models.CharField(primary_key=True, max_length=4)

    class Meta:
        managed = False
        db_table = 'annee'

class Detail(models.Model):
    iddetail = models.AutoField(primary_key=True)
    nofacture = models.ForeignKey('Facture', models.DO_NOTHING, db_column='nofacture')
    codeproduit = models.ForeignKey('Produit', models.DO_NOTHING, db_column='codeproduit')

    class Meta:
        managed = False
        db_table = 'detail'
        unique_together = (('nofacture', 'codeproduit'),)

class Facture(models.Model):
    nofacture = models.CharField(primary_key=True, max_length=50)
    nompays = models.ForeignKey('Pays', models.DO_NOTHING, db_column='nompays')
    datefacture = models.DateField()

    class Meta:
        managed = False
        db_table = 'facture'


class Histopays(models.Model):
    idhistopays = models.AutoField(primary_key=True)
    nompays = models.ForeignKey('Pays', models.DO_NOTHING, db_column='nompays')
    anneevente = models.ForeignKey(Annee, models.DO_NOTHING, db_column='anneevente')
    qtachat = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'histopays'
        unique_together = (('nompays', 'anneevente'),)


class Histoproduit(models.Model):
    idhistoproduit = models.AutoField(primary_key=True)
    codeproduit = models.ForeignKey('Produit', models.DO_NOTHING, db_column='codeproduit')
    anneevente = models.ForeignKey(Annee, models.DO_NOTHING, db_column='anneevente')
    qtvente = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'histoproduit'
        unique_together = (('codeproduit', 'anneevente'),)


class Pays(models.Model):
    nompays = models.CharField(primary_key=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'pays'


class Produit(models.Model):
    codeproduit = models.CharField(primary_key=True, max_length=50)
    description = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'produit'
