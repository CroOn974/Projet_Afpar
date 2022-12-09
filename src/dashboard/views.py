from django.shortcuts import render, redirect
from .forms import ImportVente
from dashboard.models import Produit, Pays, Facture, Detail, Annee, Histopays, Histoproduit
from django.db.models import Count
from django.db.models.functions import TruncYear
import pandas
import os
from sqlalchemy import create_engine
from django.db import connection
from django.contrib.auth.decorators import login_required



# Create your views here.
@login_required(login_url='/auth')
def home (request):
    return render(request, 'dashboard/index.html')

@login_required(login_url='/auth')
def importCsv (request):

    if request.method == 'POST':

        form = ImportVente(request.POST, request.FILES)

        if form.is_valid():

            #verifie si le répertoire existe, s'il n'existe pas on le crée
            monRepertoire = 'dashboard/upload/'
            pourAutorise = request.POST['pourField']

            addRepertoire(monRepertoire)
            delFichier(monRepertoire)
            addFichier(monRepertoire,request.FILES["collabField"])

            listeFichiers = getListeFichiers(monRepertoire)
            for fich in listeFichiers :
                print(fich)
                etatFichier = verifFichier( monRepertoire + fich, pourAutorise)


            if int(pourAutorise) < etatFichier['Pourcentage de donnée restant']:

                return redirect('savecsv')

            else:

                return render(request, "dashboard/import.html", {"form": form, "bugs":etatFichier})

    form = ImportVente()
    return render(request, "dashboard/import.html", {"form": form,})

@login_required(login_url='/auth')
def saveCsv (request):
    monRepertoire = 'dashboard/upload/'
    listeFichiers = getListeFichiers(monRepertoire)

    for fich in listeFichiers :
        print(fich)
        normeFichier( monRepertoire + fich,)

    return redirect('importcsv')



#-------------------------------------------------------------------
#                          NORMALISATION
# ------------------------------------------------------------------

# verifie si le répertoire existe, s'il n'existe pas on le crée
def addRepertoire(monRepertoire):

    if not os.path.exists(monRepertoire):
        os.makedirs(monRepertoire)

# suprime le contenue du repertoire
def delFichier(monRepertoire):

    for f in os.listdir(monRepertoire):
        os.remove(os.path.join(monRepertoire, f))

# ajoute fichier au répertoire
def addFichier(monRepertoire,f):  
    with open(monRepertoire + f.name, 'wb+') as destination:  
        for chunk in f.chunks():
            destination.write(chunk)

# récupère la liste des fichier upload
def  getListeFichiers(dossier):
    listeFichiers = []
    for (repertoire, sousRepertoires, fichiers) in os.walk(dossier):
        listeFichiers.extend(fichiers)
        break                             
    return listeFichiers

# normalise le fichier
def verifFichier(fichier, pourcentage):

    fichier = pandas.read_csv(fichier, encoding= 'unicode_escape')
    #renomme colonnes
    fichier.rename(columns = {'InvoiceNo':'nofacture', 'StockCode':'codeproduit', 'Description':'description', 'Quantity':'quantite', 'InvoiceDate':'datefacture', 'UnitPrice':'prixUnitaire', 'CustomerID':'idClient', 'Country':'nompays'}, inplace = True)
    
    #nombre de ligne dans ce le fichier en cour
    nbLigneStart = len(fichier)

    fichier = delDoublon(fichier)
    # nombre de ligne en doublon
    nbdelDoublon = nbLigneStart - len(fichier)
    nbLigneRestant = len(fichier)

    fichier = delQuantiteNegatif(fichier)
    # nombre de ligne contenant des quantité négatif
    nbdelQuantiteNegatif = nbLigneRestant - len(fichier)
    nbLigneRestant = len(fichier)

    fichier = delProbPays(fichier)
    # nombre de ligne ou le nom du pays a un problème
    nbdelProbPays = nbLigneRestant - len(fichier)
    nbLigneRestant = len(fichier)
    
    fichier = delProcCodeProduit(fichier)
    # nombre de ligne ou le code produit a un problème  et les produit sans description
    nbdelProbProduit = nbLigneRestant - len(fichier)
    nbLigneRestant = len(fichier)
    
    fichier = delProbDate(fichier)
    # nombre de ligne ou le code produit a un problème  et les produit sans description
    nbdelProbDate = nbLigneRestant - len(fichier)
    nbLigneRestant = len(fichier)
    

    pourRestant = nbLigneRestant * 100 / nbLigneStart

    etatFichier = {
        'Nombre de ligne initial ': nbLigneStart,
        'Nombre de ligne en double ': nbdelDoublon,
        'Nombre de reboursement ': nbdelQuantiteNegatif,
        'Nombre de code produit ': nbdelProbProduit,
        'Nombre de ligne avec des problemes de date': nbdelProbDate,
        'Pourcentage de donnée restant': pourRestant
    }

    return etatFichier


# normalise le fichier
def normeFichier(fichier):

    fichier = pandas.read_csv(fichier, encoding= 'unicode_escape')
    #renomme colonnes
    fichier.rename(columns = {'InvoiceNo':'nofacture', 'StockCode':'codeproduit', 'Description':'description', 'Quantity':'quantite', 'InvoiceDate':'datefacture', 'UnitPrice':'prixUnitaire', 'CustomerID':'idClient', 'Country':'nompays'}, inplace = True)
    
    fichier = delDoublon(fichier)

    fichier = delQuantiteNegatif(fichier)

    fichier = delProbPays(fichier)

    fichier = delProcCodeProduit(fichier)

    fichier = delProbDate(fichier)

    insertFichier(fichier)

# delete les doublon sur la combianaison(noFacture,codeProduit)
def delDoublon(fichier):

    return fichier.drop_duplicates(subset=['nofacture','codeproduit'])

# delete les ligne ou les quantité sont négatif
def delQuantiteNegatif(fichier):

    return  fichier.drop(fichier[(fichier['quantite'] < 0)].index)

# delete les ligne ou les nom des pays on un problème
def delProbPays(fichier):

    return fichier.drop(fichier.loc[(fichier['nompays']=="Unspecified")|(fichier['nompays']=="European Community")|(fichier['nompays']=="Channel Islands")].index)

# delete les ligne ou le code produit est incorrecte et les produit sans description
def delProcCodeProduit(fichier):

    delProd1 = fichier.drop(fichier.loc[fichier['codeproduit'].str.len() > 6].index)
    delProd2 = delProd1.drop(delProd1.loc[delProd1['codeproduit'].str.len() < 5].index)
    return  delProd2.dropna(subset=['description'])

def delProbDate(fichier):

    delDate = fichier
    delDate.datefacture = pandas.to_datetime(delDate.datefacture, format='%m/%d/%Y %H:%M', errors="coerce")
    return delDate.dropna(subset=['datefacture'])


#-------------------------------------------------------------------
#                               BDD
# ------------------------------------------------------------------
# connexion bdd
def conDb():
    try:
        conn = create_engine('postgresql://postgres:0000@localhost:5432/afpar')
        return conn
    except:
        print('prob connexion')
    

def insertFichier(fichier):

    insertProduit(fichier)

    insertPays(fichier)

    insertFacture(fichier)

    insertDetail(fichier)

    histoPays()

    histoProduit()

# insert produit
def insertProduit(fichier):

    # récupere produit existant
    existProduit = pandas.DataFrame(list(Produit.objects.all().values()))
    # existProduit = existProduit[['codeproduit','description']]

    # produit contenue dans le nouveau fichier
    produits = fichier[['codeproduit','description']]
    produits = produits.drop_duplicates(subset=['codeproduit'])

    # concat les 2 dataframe et delete les doublon
    newProduit = pandas.concat([existProduit,produits,existProduit]).drop_duplicates(keep=False)

    engine = conDb()

    try:
        newProduit.to_sql('produit', engine, if_exists='append', index=False)
    except:
        print('probleme insertProduit')

# insert pays
def insertPays(fichier):

    # récupere pays existant
    existPays = pandas.DataFrame(list(Pays.objects.all().values()))
    
    # pays contenue dans le nouveau fichier
    pays = fichier[['nompays']]
    pays = pays.drop_duplicates(subset=['nompays'])

    # concat les 2 dataframe et delete les doublon
    newPays = pandas.concat([existPays,pays,existPays]).drop_duplicates(keep=False)

    engine = conDb()

    try:
        newPays.to_sql('pays', engine, if_exists='append', index=False)
    except:
        print('probleme insertPays')

# insert facture
def insertFacture(fichier):

    # récupere facture existant
    existFacture = pandas.DataFrame(list(Facture.objects.all().values()))
    existFacture.rename(columns = {'nompays_id' : 'nompays'}, inplace = True)

    # facture contenue dans le nouveau fichier
    facture = fichier[['nofacture','nompays','datefacture']]
    facture = facture.drop_duplicates(subset=['nofacture'])

    # concat les 2 dataframe et delete les doublon
    newFacture = pandas.concat([existFacture,facture,existFacture]).drop_duplicates(subset=['nofacture'],keep=False)

    engine = conDb()

    try:
        newFacture.to_sql('facture', engine, if_exists='append', index=False)
    except:
        print('probleme insertFacture')

# insert detail
def insertDetail(fichier):

    # récupere detail commandes existant
    existDetails = pandas.DataFrame(list(Detail.objects.all().values()))
    existDetails.rename(columns = {'nofacture_id' : 'nofacture','codeproduit_id' : 'codeproduit'}, inplace = True)
    
    # detail commandes contenue dans le nouveau fichier
    details = fichier[['nofacture','codeproduit']]

    # concat les 2 dataframe et delete les doublon
    newDetails = pandas.concat([existDetails,details,existDetails]).drop_duplicates(keep=False)

    engine = conDb()

    try:
        newDetails.to_sql('detail', engine, if_exists='append', index=False)
    except:
        print('probleme insertDetail')


def histoPays():

    # récupere le nombre de vente par pays par année
    histoPays = pandas.DataFrame(list(Facture.objects.annotate(anneevente=TruncYear('datefacture')).values('nompays','anneevente').annotate(qtachat=Count('nompays')).order_by()))
    histoPays['anneevente'] = pandas.DatetimeIndex(histoPays.anneevente).year

    Histopays.objects.all().delete()
    
    insertAnnee(histoPays)
    # histoPays['anneevente']= histoPays['anneevente'].astype(str)
    print(histoPays)

    try:
        engine = conDb()
        histoPays.to_sql('histopays', engine, if_exists='append', index=False)
    except:
        print('probleme histoPays')


def histoProduit():

    # recupére en dbb le nombre de vente par produit par année
    Histoproduit.objects.all().delete()

    try:
        cursor=connection.cursor()
        cursor.execute("select detail.codeproduit, date_trunc('year', datefacture)as df, count(*) from detail inner join facture on facture.nofacture = detail.nofacture group by (detail.codeproduit,df)")
        histoProduits=pandas.DataFrame(list(cursor.fetchall()))
        histoProduits.columns = ["codeproduit", "anneevente", "qtvente"]
        histoProduits['anneevente'] = pandas.DatetimeIndex(histoProduits.anneevente).year

    except:
        print('probleme histoProduit')

    # inscrit ce nombre en bdd pour pouvoir l'affiché lus rapidement plus tard
    try:
        engine = conDb()
        histoProduits.to_sql('histoproduit', engine, if_exists='append', index=False)
    except:
        print('probleme histoPays')

 
def insertAnnee(fichier):

    try:
        # récuoére les année deja présente en bdd
        existAnnée = pandas.DataFrame(list(Annee.objects.all().values()))
        # existAnnée['anneevente'] = existAnnée['anneevente'].dt.year.astype(str)
        
    except:
        print("Probleme pour récupéré les années")

    # récupére les année dans le new fichier
    annee = fichier.drop_duplicates(subset=['anneevente'])
    #annee['anneevente'] = annee['anneevente'].dt.year.astype(str)
    
    
    print(annee.info)
    # concatene les 3 pour enlevé les doublon
    newAnnee = pandas.concat([existAnnée,annee,existAnnée]).drop_duplicates(subset=['anneevente'],keep=False)
    newAnnee = newAnnee['anneevente']
    
    print(newAnnee)

    try:
        engine = conDb()
        newAnnee.to_sql('annee', engine, if_exists='append', index=False)
    except:
         print('probleme insertAnnee')

