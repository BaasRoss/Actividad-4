import plotly.express as px
from dash import Dash, dcc, html
import json
import urllib.request
import ssl
import certifi
import unicodedata
from dataprocessing import *
 
# Cargar datos procesados
totales_dept = muertespordepartamento()
totales_mes = muertespormes()
totales_ciudad = top_homicidiosporciudad()
 
# Cargar el GeoJSON de departamentos de Colombia
url_geo = "https://raw.githubusercontent.com/caticoa3/colombia_mapa/master/co_2018_MGN_DPTO_POLITICO.geojson"

ctx = ssl.create_default_context(cafile=certifi.where())
with urllib.request.urlopen(url_geo, context=ctx) as response:
    departamentos_geo = json.load(response)
 
# Normalizar nombres de departamentos (sin tildes ni espacios)
def normalizar(texto):
    if isinstance(texto, str):
        texto = texto.strip().upper()
        texto = (
            unicodedata.normalize("NFKD", texto)
            .encode("ascii", errors="ignore")
            .decode("utf-8")
        )
        return texto
    return texto
 
totales_dept["DEPARTAMENTO"] = totales_dept["DEPARTAMENTO"].apply(normalizar)
 
for feature in departamentos_geo["features"]:
    feature["properties"]["DPTO_CNMBR"] = normalizar(feature["properties"]["DPTO_CNMBR"])
 
geo_departamentos = [f["properties"]["DPTO_CNMBR"] for f in departamentos_geo["features"]]
df_departamentos = totales_dept["DEPARTAMENTO"].unique()
no_coinciden = [d for d in df_departamentos if d not in geo_departamentos]
print("\nDepartamentos que no coinciden con el geojson:", no_coinciden)
 
# Crear mapa 
fig_mapa = px.choropleth_mapbox(
    totales_dept,
    geojson=departamentos_geo,
    locations="DEPARTAMENTO",
    featureidkey="properties.DPTO_CNMBR",  # <- Campo correcto
    color="muertes",
    color_continuous_scale="Reds",
    mapbox_style="carto-positron",
    zoom=4,
    center={"lat": 4.5709, "lon": -74.2973},
    opacity=0.7,
    title="Distribución de muertes por departamento (2019)"
)
 
# Gráfico de barras 
fig_bar_dept = px.bar(
    totales_dept.head(10),
    x="DEPARTAMENTO",
    y="muertes",
    title="Top 10 departamentos con más muertes (2019)",
    labels={"DEPARTAMENTO": "Departamento", "muertes": "Número de muertes"}
)
 
# Gráfico de líneas
fig_line_mes = px.line(
    totales_mes,
    x="MES",
    y="muertes",
    title="Distribución mensual de muertes (2019)",
    markers=True,
    labels={"MES": "Mes", "muertes": "Número de muertes"}
)
 
# Gráfico de barras 
fig_bar_ciudad = px.bar(
    totales_ciudad,
    x="MUNICIPIO",
    y="muertes",
    title="Top 5 ciudades con más homicidios",
    labels={"MUNICIPIO": "Municipio", "muertes": "Número de muertes"}
)
 
# Aplicación Dash

app = Dash(__name__)
app.title = "Mortalidad en Colombia 2019"
 
app.layout = html.Div(
    style={"fontFamily": "Arial", "maxWidth": "1000px", "margin": "20px auto"},
    children=[
        html.H1("Mortalidad en Colombia 2019", style={"textAlign": "center"}),
 
        html.H3("Distribución por departamento (Mapa)"),
        dcc.Graph(figure=fig_mapa),
 
        html.H3("Top 10 departamentos con más muertes (2019)"),
        dcc.Graph(figure=fig_bar_dept),
 
        html.H3("Distribución por mes"),
        dcc.Graph(figure=fig_line_mes),
 
        html.H3("Top 5 ciudades con más homicidios"),
        dcc.Graph(figure=fig_bar_ciudad),
    ]
)
 
if __name__ == "__main__":
    app.run(debug=True)
