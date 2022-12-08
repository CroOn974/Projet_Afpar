# from dash import Dash, dcc, html, Input, Output
# import plotly.express as px
# from django_plotly_dash import DjangoDash
# import pandas as pd
# import dash_bootstrap_components as dbc
# from dashboard.models import Produit, Pays, Facture, Detail, Annee, Histopays, Histoproduit 


# bootstrap_theme=[dbc.themes.BOOTSTRAP,'https://use.fontawesome.com/releases/v5.9.0/css/all.css']

# print('1')
# # histoProduit = pd.DataFrame(list(Histoproduit.objects.all().values()))
# # print(histoProduit)
# print('1')
# histoPays = Histopays.objects.all().values()
# print(histoPays)
# print('1')


# app = DjangoDash('SimpleExample',external_stylesheets=bootstrap_theme )

# df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

# # app.layout = html.Div([
# #     html.Div([

# #         html.Div([
# #             dcc.Dropdown(
# #                 df['Indicator Name'].unique(),
# #                 'Fertility rate, total (births per woman)',
# #                 id='xaxis-column'
# #             ),
# #         ], style={'width': '48%', 'display': 'inline-block'}),

# #     ]),

# #     dcc.Graph(id='indicator-graphic'),

# #     dcc.Slider(
# #         histoProduit['anneevente'].min(),
# #         histoProduit['anneevente'].max(),
# #         step=None,
# #         id='year--slider',
# #         value=histoProduit['anneevente'].max(),
# #         marks={str(annee): str(annee) for annee in histoProduit['anneevente']},

# #     )
# # ])


# # @app.callback(
# #     Output('indicator-graphic', 'figure'),
# #     Input('xaxis-column', 'value'),
# #     Input('yaxis-column', 'value'),
# #     Input('xaxis-type', 'value'),
# #     Input('yaxis-type', 'value'),
# #     Input('year--slider', 'value'))
# # def update_graph(xaxis_column_name, yaxis_column_name,
# #                  xaxis_type, yaxis_type,
# #                  year_value):
    
# #     if dff['Indicator Name'] == "produit":
# #         dff = df[histoProduit['anneevente'] == year_value]

# #     else:
# #         dff = df[histoPays['anneevente'] == year_value]


# #     fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
# #                      y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
# #                      hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

# #     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

# #     fig.update_xaxes(title=xaxis_column_name,
# #                      type='linear' if xaxis_type == 'Linear' else 'log')

# #     fig.update_yaxes(title=yaxis_column_name,
# #                      type='linear' if yaxis_type == 'Linear' else 'log')

# #     return fig


# # if __name__ == '__main__':
# #     app.run_server(debug=True)