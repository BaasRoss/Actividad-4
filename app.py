import pandas as pd
import json as js
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output
# --------- Cargar datos ---------
df = pd.read_excel("Data/Anexo1.NoFetal2019_CE_15-03-23.xlsx", engine="openpyxl")
codigos = pd.read_excel("Data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx", engine="openpyxl",header=8)
divipola = pd.read_excel("Data\Divipola_CE_.xlsx", engine="openpyxl")

# mostrar columnas (útil para saber cómo se llaman)
print("Columns NoFetal2019:", df.head())
print("Columns CodigosDeMuerte:", codigos.head())
print("Columns Divipola:", divipola.head())
