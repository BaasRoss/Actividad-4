import plotly.express as px
from dash import Dash, dcc, html, dash_table
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
top_menos_mortandad = top_ciudadesmenosmuertes()
top_causas = top_causasdemuerte()
muertesporsexo = muertesdepartamentoysexo()
 
# Cargar el GeoJSON de departamentos de Colombia
url_geo = "https://raw.githubusercontent.com/caticoa3/colombia_mapa/master/co_2018_MGN_DPTO_POLITICO.geojson"

ctx = ssl.create_default_context(cafile=certifi.where())
with urllib.request.urlopen(url_geo, context=ctx) as response:
    departamentos_geo = json.load(response)
 
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
    featureidkey="properties.DPTO_CNMBR", 
    color="muertes",
    color_continuous_scale="Reds",
    mapbox_style="carto-positron",
    zoom=4,
    center={"lat": 4.5709, "lon": -74.2973},
    opacity=0.7,
    title="Distribución de muertes por departamento (2019)"
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

# Gráfico circular 
fig_pie_menos = px.pie(
    top_menos_mortandad,
    names="MUNICIPIO",
    values="muertes",
    title="Top 10 ciudades con menos muertes",
    labels={"MUNICIPIO": "Municipio", "muertes": "Número de muertes"},
    hole=0.3
)

# Tabla
table_causas = dash_table.DataTable(
    data=top_causas.to_dict("records"),
    columns=[{"name": col, "id": col} for col in top_causas.columns],
    page_size=10,
    sort_action="native",
    filter_action="native",
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "left", "padding": "5px", "whiteSpace": "normal"},
    style_header={"fontWeight": "bold"}
)

# Preparar gráfico de barras apiladas por departamento y sexo
sexo_map = {'1': 'Masculino', '2': 'Femenino', '3': 'Indeterminado'}
# `df` viene de dataprocessing (se importó con `from dataprocessing import *`)
df_tmp = df.copy()
df_tmp['SEXO'] = df_tmp['SEXO'].astype(str).str.strip().replace(sexo_map).fillna('Indeterminado')
df_tmp['DEPARTAMENTO'] = df_tmp['DEPARTAMENTO'].apply(normalizar)
dept_sexo_counts = (
    df_tmp
    .groupby(['DEPARTAMENTO', 'SEXO'], dropna=False)
    .size()
    .reset_index(name='muertes')
)
# Ordenar departamentos por total de muertes para mostrar en el mismo orden
orden_dept = totales_dept['DEPARTAMENTO'].tolist()
dept_sexo_counts['DEPARTAMENTO'] = pd.Categorical(dept_sexo_counts['DEPARTAMENTO'], categories=orden_dept, ordered=True)
dept_sexo_counts = dept_sexo_counts.sort_values('DEPARTAMENTO')

fig_stacked = px.bar(
    dept_sexo_counts,
    x='DEPARTAMENTO',
    y='muertes',
    color='SEXO',
    title='Muertes por departamento y sexo (apilado)',
    labels={'DEPARTAMENTO': 'Departamento', 'muertes': 'Número de muertes', 'SEXO': 'Sexo'}
)
fig_stacked.update_layout(barmode='stack', xaxis={'categoryorder':'array', 'categoryarray': orden_dept}, margin={'t':40,'b':150}, legend_title_text='Sexo')

# Aplicación Dash

app = Dash(__name__)
app.title = "Mortalidad en Colombia 2019"
 
app.layout = html.Div(
    style={"fontFamily": "Arial", "maxWidth": "1000px", "margin": "20px auto"},
    children=[
        html.H1("Mortalidad en Colombia 2019", style={"textAlign": "center"}),
 
        html.H3("Distribución por departamento (Mapa)"),
        dcc.Graph(figure=fig_mapa),
        
        html.H3("Distribución por mes"),
        dcc.Graph(figure=fig_line_mes),
        
        html.H3("Top 5 ciudades con más homicidios"),
        dcc.Graph(figure=fig_bar_ciudad),

        html.H3("Top 10 ciudades con menos muertes"),
        dcc.Graph(figure=fig_pie_menos),

        html.H3("Top 10 principales causas de muerte"),
        table_causas,

        html.H3("Muertes por departamento y sexo (apilado)"),
        dcc.Graph(figure=fig_stacked),

    ]
)
 
if __name__ == "__main__":
    app.run(debug=True)
