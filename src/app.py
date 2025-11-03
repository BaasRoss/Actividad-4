import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output
import json

import urllib.request

from dataprocessing import *

totales_dept =  muertespordepartamento()
totales_mes = muertespormes()
totales_ciudad = top_homicidiosporciudad()

url_geo = "https://raw.githubusercontent.com/jacasta2/colombian_map/master/mapa_departamentos.json"

with urllib.request.urlopen(url_geo) as response:

    departamentos_geo = json.load(response)
    
    print(departamentos_geo)

# --------- Grafico de pastel ---------

# --------- Tabla ---------

# --------- Grafico de barras apiladas --------

# --------- Histograma ---------





# --------- Aplicacion Dash ---------

app = Dash(__name__)

app.title = "Mortalidad en Colombia 2019"

app.layout = html.Div(style={"fontFamily": "Arial", "maxWidth": "1000px", "margin": "20px auto"}, children=[

    html.H1("Mortalidad en Colombia 2019", style={"textAlign": "center"}),
    
# --------- Mapa ---------

html.H3("Distribución por departamento"),

    dcc.Graph(figure=px.bar(

        totales_dept.head(10),

        x="DEPARTAMENTO",

        y="muertes",

        title="Top 10 departamentos con más muertes (2019)",
        
        labels={"DEPARTAMENTO": "Departamento", "muertes": ""}
        

    )),

# --------- Grafico de lineas ---------
 
html.H3("Distribución por mes"),

 dcc.Graph(

     figure=px.line(

         totales_mes,

         x="MES",

         y="muertes",

         title="Distribución mensual de muertes (2019)",

         markers=True,  # Puntos en la línea

         labels={"MES": "Mes", "muertes": "Número de muertes"}

     )

 ),
 
 # --------- Grafico de barras ---------
 
 html.H3("Top 5 ciudades con más homicidios"),

     dcc.Graph(figure=px.bar(

         totales_ciudad,

         x="MUNICIPIO",

         y="muertes",

         title="Homicidios por ciudad",
         
         labels={"MUNICIPIO": "Municipio", "muertes": "Número de muertes"}

     ))
 ])


if __name__ == "__main__":
     app.run(debug=True)