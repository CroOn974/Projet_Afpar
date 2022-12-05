from django.shortcuts import render, redirect
from .forms import ImportVente
from dashboard.models import Produit, Pays, Facture, Detail
import pandas
import os
from sqlalchemy import create_engine


# Create your views here.

def dashboard (request):
    return render(request, 'dashboard/index.html')


def importCsv (request):

    if request.method == 'POST':

        form = ImportVente(request.POST, request.FILES)

        if form.is_valid():

            #verifie si le répertoire existe, s'il n'existe pas on le crée
            monRepertoire = 'dashboard/upload/'

            addRepertoire(monRepertoire)

            addFichier(monRepertoire,request.FILES["collabField"])

            listeFichiers = getListeFichiers(monRepertoire)

            for fich in listeFichiers :
                print(fich)
                normeFichier( monRepertoire + fich)
    
            delFichier(monRepertoire)

        redirect("importcsv")

    else:

        form = ImportVente()

    return render(request, "dashboard/import.html", {"form": form})

#____________________________________________________________________
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
def normeFichier(fichier):

    fichier = pandas.read_csv(fichier, encoding= 'unicode_escape')
    #renomme colonnes
    fichier.rename(columns = {'InvoiceNo':'nofacture', 'StockCode':'codeproduit', 'Description':'description', 'Quantity':'quantite', 'InvoiceDate':'datefacture', 'UnitPrice':'prixUnitaire', 'CustomerID':'idClient', 'Country':'nompays'}, inplace = True)
    
    #nombre de ligne dans ce le fichier en cour
    nbLigneStart = len(fichier)

    fichier = delDoublon(fichier)
    # nombre de ligne en doublon
    nbdelDoublon = nbLigneStart - len(fichier)

    fichier = delQuantiteNegatif(fichier)
    # nombre de ligne contenant des quantité négatif
    nbdelQuantiteNegatif = nbdelDoublon - len(fichier)

    fichier = delProbPays(fichier)
    # nombre de ligne ou le nom du pays a un problème
    nbdelProbPays = nbdelQuantiteNegatif - len(fichier)

    fichier = delProcCodeProduit(fichier)
    # nombre de ligne ou le code produit a un problème  et les produit sans description
    nbdelProbProduit = nbdelProbPays - len(fichier)

    fichier = delProbDate(fichier)
    # nombre de ligne ou le code produit a un problème  et les produit sans description
    nbdelProbDate = nbdelProbProduit - len(fichier)

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


#____________________________________________________________________
#BDD
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

    #insertDetail(fichier)

# insert produit
def insertProduit(fichier):

    # récupere produit existant
    existProduit = pandas.DataFrame(list(Produit.objects.all().values()))
    # existProduit = existProduit[['codeproduit','description']]

    # produit contenue dans le nouveau fichier
    produits = fichier[['codeproduit','description']]
    produits = produits.drop_duplicates(subset=['codeproduit'])

    # concat les 2 dataframe et delete les doublon
    newProduit = pandas.concat([existProduit,produits]).drop_duplicates(keep=False)

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
    newPays = pandas.concat([existPays,pays]).drop_duplicates(keep=False)

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
    newFacture = pandas.concat([existFacture,facture]).drop_duplicates(subset=['nofacture'],keep=False)
    print(newFacture)

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
    newDetails = pandas.concat([existDetails,details]).drop_duplicates(keep=False)

    engine = conDb()

    try:
        newDetails.to_sql('detail', engine, if_exists='append', index=False)
    except:
        print('probleme insertDetail')




