from django.db import models

# Create your models here.

class Datevente(models.Model):
    annee = models.DateField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'datevente'


class Detail(models.Model):
    iddetail = models.AutoField(primary_key=True)
    nofacture = models.ForeignKey('Facture', models.DO_NOTHING, db_column='nofacture', blank=True, null=True)
    noproduit = models.ForeignKey('Produit', models.DO_NOTHING, db_column='noproduit', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detail'
        unique_together = (('nofacture', 'noproduit'),)


class Facture(models.Model):
    nofacture = models.IntegerField(primary_key=True)
    datefacturation = models.DateField()
    nompays = models.ForeignKey('Pays', models.DO_NOTHING, db_column='nompays')

    class Meta:
        managed = False
        db_table = 'facture'


class Histopays(models.Model):
    idhistopays = models.AutoField(primary_key=True)
    nompays = models.ForeignKey('Pays', models.DO_NOTHING, db_column='nompays', blank=True, null=True)
    annee = models.ForeignKey(Datevente, models.DO_NOTHING, db_column='annee', blank=True, null=True)
    qtacheter = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'histopays'
        unique_together = (('nompays', 'annee'),)


class Histoproduit(models.Model):
    idhistoprod = models.AutoField(primary_key=True)
    noproduit = models.ForeignKey('Produit', models.DO_NOTHING, db_column='noproduit', blank=True, null=True)
    annee = models.ForeignKey(Datevente, models.DO_NOTHING, db_column='annee', blank=True, null=True)
    qtvendu = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'histoproduit'
        unique_together = (('annee', 'noproduit'),)


class Pays(models.Model):
    nompays = models.CharField(primary_key=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'pays'


class Produit(models.Model):
    codeproduit = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'produit'
