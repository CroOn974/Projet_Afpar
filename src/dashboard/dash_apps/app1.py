from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_bootstrap_components as dbc
from dashboard.models import Produit, Pays, Facture, Detail, Annee, Histopays, Histoproduit 


bootstrap_theme=[dbc.themes.BOOTSTRAP,'https://use.fontawesome.com/releases/v5.9.0/css/all.css']

histoProduit = pd.DataFrame(list(Histoproduit.objects.all().values()))
histoProduit.rename(columns = {'idhistoproduit' : 'histo', 'codeproduit_id': 'indicator', 'anneevente_id': 'annee', 'qtvente' : 'quantite'}, inplace = True)
histoProduit['histo'] = 'produit'

histoPays = pd.DataFrame(list(Histopays.objects.all().values()))
histoPays.rename(columns = {'idhistopays' : 'histo', 'nompays_id': 'indicator', 'anneevente_id': 'annee', 'qtachat' : 'quantite'}, inplace = True)
histoPays['histo'] = 'pays'

df = pd.concat([histoProduit,histoPays])


app = DjangoDash('SimpleExample',external_stylesheets=bootstrap_theme )


import plotly.graph_objects as go

fig = go.Figure()

app.layout = html.Div([

    html.Div([
            dcc.Dropdown(
                df['histo'].unique(),
                'produit',
                id='histo-input'
            )], style={'width': '48%', 'display': 'inline-block'}),


    html.Div([dcc.Graph(id='bar_graph',figure=fig)]),

    dcc.Slider(
        df['annee'].min(),
        df['annee'].max(),
        step=None,
        id='year--slider',
        value=df['annee'].max(),
        marks={str(year): str(year) for year in df['annee'].unique()},

    )


             
])
# https://plotly.com/python/click-events/ ON CLICK
@app.callback(

    Output('bar_graph', 'figure'),
    Input('histo-input', 'value'),
    Input('year--slider', 'value')
    )
def update_bar(histo_input,year_value):

    print(year_value)
    print(type(year_value))
    dff = df.loc[df['annee'] == str(year_value)]

    print(dff)
    #Magnitude vs Number
    if histo_input == "pays": 
        print(dff)
        qtproduit = dff.loc[dff['histo'] == "pays"]
        print(qtproduit)

        fig = go.Figure(go.Bar(x=qtproduit['indicator'],
                               y=qtproduit['quantite'],
                               marker_color = 'green',
                               
                               ),
                        go.Layout(  title='Nombre commande par pays',
                                    title_x = 0.5, 
                                    xaxis=dict( tickangle=90,
                                                tickmode='linear',
                                                tick0=0.1,
                                                dtick=0.1
                                    )),

                        )
        fig.update_layout(barmode='stack', bargap=0.1,bargroupgap=0.1)

    #Depth vs Number
    elif histo_input == "produit": 
        
        qtproduit = dff.loc[dff['histo'] == "produit"]

        fig = go.Figure(go.Bar(x=qtproduit['indicator'],
                               y=qtproduit['quantite'],
                               marker_color = 'blue',
                               
                               )
                        )

    else:
        pass
    
    return fig
        
