import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

load_figure_template("darkly")

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.DARKLY])

# server = app.server

df_data = pd.read_csv("supermarket_sales.csv")
df_data.rename(columns={"gross income": "Faturamento", "Rating": "Avaliação"},
               inplace=True)

lista_cidades = df_data["City"].value_counts().index

# ============ layout =========================
app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Img(src="./assets/logo_dark.png"),
                html.Hr(),
                html.H5("Cidades:"),
                dcc.Checklist(id="chk_cidade",
                              options=lista_cidades,
                              value=lista_cidades),
                html.H5("Tipo de Análise:", style={"margin-top": "10px"}),
                dcc.RadioItems(id="rdio_var",
                               options=["Faturamento", "Avaliação"],
                               value="Faturamento"),
            ], style={"height": "90vh", "margin": "20px", "padding": "15px"}),
        ], sm=2),
        dbc.Col([
            dbc.Row([
                dbc.Col([dcc.Graph(id="graph_fat_cidade")], sm=4),
                dbc.Col([dcc.Graph(id="graph_fat_genero")], sm=4),
                dbc.Col([dcc.Graph(id="graph_fat_pagto")], sm=4),
            ]),
            dbc.Row([dcc.Graph(id="graph_fat_data")]),
            dbc.Row([dcc.Graph(id="graph_fat_prod")]),
        ], sm=10)
    ]),
])


# ============ Callbacks =========================
@app.callback([
    Output(component_id="graph_fat_cidade", component_property="figure"),
    Output(component_id="graph_fat_pagto", component_property="figure"),
    Output(component_id="graph_fat_prod", component_property="figure"),
    Output(component_id="graph_fat_genero", component_property="figure"),
    Output(component_id="graph_fat_data", component_property="figure")
], [
    Input(component_id="chk_cidade", component_property="value"),
    Input(component_id="rdio_var", component_property="value"),
])
def atualiza_grafico(cidades, tipo):
    operacao = np.sum if tipo == "Faturamento" else np.mean
    df_filtrado = df_data[df_data["City"].isin(cidades)]
    df_cidade = (
        df_filtrado.groupby("City")[tipo]
        .apply(operacao)
        .to_frame()
        .reset_index()
    )
    df_pagamento = (
        df_filtrado.groupby("Payment")[tipo]
        .apply(operacao)
        .to_frame()
        .reset_index()
    )
    df_produto = (
        df_filtrado.groupby(["Product line", "City"])[tipo]
        .apply(operacao)
        .to_frame()
        .reset_index()
    )
    df_genero = (
        df_filtrado.groupby(["Gender", "City"])[tipo]
        .apply(operacao)
        .to_frame()
        .reset_index()
    )
    df_por_data = (
        df_filtrado.groupby("Date")[tipo]
        .apply(operacao)
        .to_frame()
        .reset_index()
    )

    fig1 = px.bar(df_cidade, x="City", y=tipo)
    fig2 = px.bar(df_pagamento, y="Payment", x=tipo, orientation="h")
    fig3 = px.bar(df_produto, y="Product line", x=tipo,
                  orientation="h", color="City", barmode="group")
    fig4 = px.bar(df_genero, y=tipo, x="Gender", color="City", barmode="group")
    fig5 = px.bar(df_por_data, x="Date", y=tipo)

    for fig in [fig1, fig2, fig4]:
        fig.update_layout(margin=dict(l=0, r=0, t=20, b=20),
                          height=200, template="darkly")

    fig3.update_layout(margin=dict(l=0, r=0, t=20, b=20),
                       height=500, template="darkly")
    fig5.update_layout(margin=dict(l=0, r=0, t=20, b=20),
                       height=500, template="darkly")

    return fig1, fig2, fig3, fig4, fig5


if __name__ == "__main__":
    app.run_server(debug=False)
