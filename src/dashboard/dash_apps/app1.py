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
                        
                        )], style={'width': '50%', 'display': 'inline-block'}),

            ]),
            
            dbc.Col([

                html.Div([
                    dcc.Dropdown(
                        'top 0 a 20',
                        0,
                        id='top-input',
                
                        )], style={'width': '50%', 'display': 'inline-block'}),

            ]),

    ]),

    dbc.Row([

            dbc.Col([

                html.Div([dcc.Graph(id='bar_graph',figure=fig)]),

                dbc.Label("Slider", html_for="slider"),
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
            
    ]),
    
])

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

    # construit le graphique
    fig = go.Figure(go.Bar(x=qtproduit['indicator'],
                            y=qtproduit['quantite'],
                            
                            
                            ),
                    go.Layout(  title='Nombre commande par '+ histo_input +'',
                                title_x = 0.5, 
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
    return [{'label': 'top '+ str(i *20) + ' à top ' + str((i+1)*20) +'', 'value': i} for i in range(int(nbPart))]


@app.callback(
    Output('pie_graph', 'figure'),
    Input('bar_graph', 'clickData'),
    Input('year-slider', 'value'),
    Input('histo-input', 'value'),
    )
def display_click_data(clickData,year_slider,histo_input):

    year_slider = str(year_slider)

    clickValue = clickData['points'][0]['label']

    if histo_input == 'produit':

        try:
            cursor=connection.cursor()
            cursor.execute("SELECT nompays,detail.codeproduit, COUNT(*) as qt from detail INNER JOIN facture on facture.nofacture = detail.nofacture WHERE detail.codeproduit ='" + clickValue + "' and TO_CHAR(datefacture, 'YYYY') = '" + year_slider + "' GROUP BY (nompays,detail.codeproduit) ORDER BY qt desc limit 10")
            data=pd.DataFrame(list(cursor.fetchall()))
            data.columns = ["name", "codeproduit", "qtvente"]
            
        except:
            print('probleme click produit')

    elif histo_input == 'pays':

        try:
            cursor=connection.cursor()
            cursor.execute("SELECT nompays,detail.codeproduit, COUNT(*) as qt from detail INNER JOIN facture on facture.nofacture = detail.nofacture inner join produit on produit.codeproduit = detail.codeproduit WHERE nompays ='" + clickValue + "' and TO_CHAR(datefacture, 'YYYY') = '" + year_slider + "' GROUP BY (nompays,detail.codeproduit) ORDER BY qt desc limit 10")
            data=pd.DataFrame(list(cursor.fetchall()))
            data.columns = ["pays", "name", "qtvente"]

        except:
            print('probleme click produit')

    return px.pie(data, values='qtvente', names='name', title=''+ clickValue +'', hole=.3)
