from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_bootstrap_components as dbc
from dashboard.models import Produit, Pays, Facture, Detail, Annee, Histopays, Histoproduit 
import math
import plotly.graph_objects as go
import dash_html_components as dhtml
from django.db import connection

bootstrap_theme=[dbc.themes.BOOTSTRAP,'https://use.fontawesome.com/releases/v5.9.0/css/all.css']

histoProduit = pd.DataFrame(list(Histoproduit.objects.all().values()))
histoProduit.rename(columns = {'idhistoproduit' : 'histo', 'codeproduit_id': 'indicator', 'anneevente_id': 'annee', 'qtvente' : 'quantite'}, inplace = True)
histoProduit['histo'] = 'produit'

histoPays = pd.DataFrame(list(Histopays.objects.all().values()))
histoPays.rename(columns = {'idhistopays' : 'histo', 'nompays_id': 'indicator', 'anneevente_id': 'annee', 'qtachat' : 'quantite'}, inplace = True)
histoPays['histo'] = 'pays'

df = pd.concat([histoProduit,histoPays])

app = DjangoDash('SimpleExample',external_stylesheets=bootstrap_theme )
app.css.append_css({ "external_url" : "/static/css/app1.css" })

fig = go.Figure()

app.layout = html.Div([

    dbc.Row([

            dbc.Col([

                html.Div([
                        dhtml.Div(id='output'),
                        dcc.Dropdown(
                            df['histo'].unique(),
                            'produit',
                            id='histo-input',
                        
                        )], style={'width': '40%', 'display': 'inline-block'}),

            ]),
            
            dbc.Col([

                html.Div([
                    dcc.Dropdown(
                        'top 0 a 20',
                        0,
                        id='top-input',
                
                        )], style={'width': '40%', 'display': 'inline-block'}),

            ]),

    ],className="g-0"),

    dbc.Row([

            dbc.Col([

                html.Div([dcc.Graph(id='bar_graph',figure=fig)]),

                dbc.Label("Année", html_for="slider"),
                dcc.Slider(
                    step=None,
                    id='year-slider',
                    value=df['annee'].min(),
                    marks={str(year): str(year) for year in df['annee'].unique()},
                ),
                
            ]), 
            dbc.Col([
                html.Div([dcc.Graph(id='pie_graph',figure=fig)]),
        ]),
            
    ],className="g-0",style={'height' : '100 vh'}),
    
],style = {'text-align': 'center'})

# https://plotly.com/python/click-events/ ON CLICK
@app.callback(

    Output('bar_graph', 'figure'),
    Input('histo-input', 'value'),
    Input('top-input', 'value'),
    Input('year-slider', 'value')
    )
def update_bar(histo_input,top_input,year_value):

    # select donnée selon l'année
    dff = df.loc[df['annee'] == str(year_value)]
 
    # select donnée selon valeur du dropdown
    qtproduit = dff.loc[dff['histo'] == histo_input]

    # classe les donnée dans l'ordre decroissant selon la quantité
    qtproduit.sort_values(by=['quantite'], inplace=True, ascending=False)

    # determine l'interval que l'on veut regardé
    topDebut = top_input * 20
    topFin = (top_input + 1) * 20
    qtproduit = qtproduit.iloc[topDebut : topFin,:]
    import numpy as np
    # construit le graphique
    fig = go.Figure(go.Bar(     x=qtproduit['indicator'],
                                y=qtproduit['quantite'],
                            
                            ),
                    go.Layout(  title='Nombre commande par '+ histo_input +'',
                                title_x = 0.5,
                                barmode='overlay' 
                            ),

                    )

    return fig


# Permet de mettre a jour le dropdown "top"
@app.callback(
    Output('top-input', 'options'),
    Input('histo-input', 'value'),
    Input('year-slider', 'value')
    )
def update_dropdown(histo_input,year_value):
    
    # select donnée selon l'année
    dff = df.loc[df['annee'] == str(year_value)]

    # select donnée selon valeur du dropdown
    qtproduit = dff.loc[dff['histo'] == histo_input]

    # dertermine le nombre de partition
    nbDec = 20
    nbPart = math.ceil(len(qtproduit) / nbDec)

    #retourne les option du dropdown
    return [{'label': 'top '+ str(1+(i *20)) + ' à top ' + str((i+1)*20) +'', 'value': i} for i in range(int(nbPart))]

# S'execute quand on click sur un bar de l'histogramme
@app.callback(
    Output('pie_graph', 'figure'),
    Input('bar_graph', 'clickData'),
    Input('year-slider', 'value'),
    Input('histo-input', 'value'),
    )
def display_click_data(clickData,year_slider,histo_input):

    year_slider = str(year_slider)

    # récupére le label de la barre
    clickValue = clickData['points'][0]['label']

    # determine si c'est un pays ou un produit
    if histo_input == 'produit':

        # récupere le top 10 des pays ayant le plus commandé ce produit
        try:
            cursor=connection.cursor()
            cursor.execute("SELECT nompays,detail.codeproduit,description, COUNT(*) as qt from detail INNER JOIN facture on facture.nofacture = detail.nofacture INNER JOIN produit on detail.codeproduit = produit.codeproduit WHERE detail.codeproduit ='" + clickValue + "' and TO_CHAR(datefacture, 'YYYY') = '" + year_slider + "' GROUP BY (nompays,detail.codeproduit,description) ORDER BY qt desc limit 10")
            data=pd.DataFrame(list(cursor.fetchall()))
            data.columns = ["name", "codeproduit","nom","qtvente"]
            clickValue = clickValue + ' : ' + data["nom"][0]


        except:
            print('probleme click produit')

    elif histo_input == 'pays':

        # récupere le top 10 des produit le plus commandé par ce pays
        try:
            cursor=connection.cursor()
            cursor.execute("SELECT nompays,detail.codeproduit,description, COUNT(*) as qt from detail INNER JOIN facture on facture.nofacture = detail.nofacture INNER JOIN produit on produit.codeproduit = detail.codeproduit WHERE nompays ='" + clickValue + "' and TO_CHAR(datefacture, 'YYYY') = '" + year_slider + "' GROUP BY (nompays,detail.codeproduit,description) ORDER BY qt desc limit 10")
            data=pd.DataFrame(list(cursor.fetchall()))
            data.columns = ["pays", "name", "description","qtvente"]
            # data['over'] = data["codeproduit"] + " : " + data["description"]
            
            # cursor.execute("SELECT nompays,COUNT(*) as qt from detail INNER JOIN facture on facture.nofacture = detail.nofacture INNER JOIN produit on detail.codeproduit = produit.codeproduit  WHERE nompays ='" + clickValue + "' and TO_CHAR(datefacture, 'YYYY') = '" + year_slider + "' GROUP BY (nompays)")
            # totalVente=pd.DataFrame(list(cursor.fetchall()))
            # totalVente.columns = ["pays","qtvente"]

            # sumData = data.sum(axis=1)
            # nbReste = totalVente['qtvente'] - sumData

            # reste = pd.DataFrame({'pays' : data['pays'][0], 'name' : 'reste', 'description' :  data['description'][0], 'qtvente': nbReste})

            # data = pd.concat([data,reste])

        except:
            print('probleme click produit')

    pie = px.pie(data, values='qtvente', names='name', title=''+ clickValue +'', hole=.3)
    pie.update_layout(title_pad_b= 100)

    # retoune le graphique
    return pie
