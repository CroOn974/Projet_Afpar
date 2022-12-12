from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_bootstrap_components as dbc
from dashboard.models import Produit, Pays, Facture, Detail, Annee, Histopays, Histoproduit 
import math
import plotly.graph_objects as go
import dash_html_components as dhtml


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

    html.Div([
            dhtml.Div(id='output'),
            dcc.Dropdown(
                df['histo'].unique(),
                'produit',
                id='histo-input'
            )], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            'top 0 a 20',
             0,
            id='top-input'
        )], style={'width': '48%', 'display': 'inline-block'}),


    html.Div([dcc.Graph(id='bar_graph',figure=fig)]),

    dcc.Slider(
        step=None,
        id='year-slider',
        value=df['annee'].min(),
        marks={str(year): str(year) for year in df['annee'].unique()},

    )

#Region.objects.annotate(invoice_details = Count('invoice__details')).order_by('-invoice_details')
             
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
                            marker_color = 'green',
                            
                            ),
                    go.Layout(  title='Nombre commande par '+ histo_input +'',
                                title_x = 0.5, 
                            ),

                    )

    fig.update_layout(barmode='stack', bargap=0.1,bargroupgap=0.1)

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





    

