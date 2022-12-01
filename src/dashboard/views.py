from django.shortcuts import render, redirect
from .forms import ImportVente
from dashboard.models import Produit
import pandas
import os

# Create your views here.

def dashboard (request):
    return render(request, 'dashboard/index.html')


def importCsv (request):

    if request.method == 'POST':

        form =  ImportVente(request.POST, request.FILES)

        if form.is_valid():

            #verifie si le répertoire existe, s'il n'existe pas on le crée
            monRepertoire = 'dashboard/upload/'

            addRepertoire(monRepertoire)

            addFichier(monRepertoire,request.FILES["collabField"])

            listeFichiers = getListeFichiers(monRepertoire)

            for fich in listeFichiers :
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
    fichier.rename(columns = {'InvoiceNo':'noFacture', 'StockCode':'codeProduit', 'Description':'description', 'Quantity':'quantite', 'InvoiceDate':'dateFacture', 'UnitPrice':'prixUnitaire', 'CustomerID':'idClient', 'Country':'pays'}, inplace = True)
    
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

    insertFichier(fichier)



    
    return

# delete les doublon sur la combianaison(noFacture,codeProduit)
def delDoublon(fichier):

    return fichier.drop_duplicates(subset=['noFacture','codeProduit'])

# delete les ligne ou les quantité sont négatif
def delQuantiteNegatif(fichier):

    return  fichier.drop(fichier[(fichier['quantite'] < 0)].index)

# delete les ligne ou les nom des pays on un problème
def delProbPays(fichier):

    return fichier.drop(fichier.loc[(fichier['pays']=="Unspecified")|(fichier['pays']=="European Community")|(fichier['pays']=="Channel Islands")].index)

# delete les ligne ou le code produit est incorrecte et les produit sans description
def delProcCodeProduit(fichier):

    delProd1 = fichier.drop(fichier.loc[fichier['codeProduit'].str.len() > 6].index)
    delProd2 = delProd1.drop(delProd1.loc[delProd1['codeProduit'].str.len() < 5].index)
    return  delProd2.dropna(subset=['description'])


#____________________________________________________________________
#BDD

def insertFichier(fichier):

    insertProduit(fichier)


def insertProduit(fichier):

    # produits = fichier[['codeProduit','description']]
    # df_records = df.to_dict('records')
    # model_instances = [MyModel(
    #     field_1=record['field_1'],
    #     field_2=record['field_2'],
    # ) for record in df_records]
    # MyModel.objects.bulk_create(model_instances)
    return