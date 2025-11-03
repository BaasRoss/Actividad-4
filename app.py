import pandas as pd
import json as js
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output

# --------- Cargar datos ---------
df = pd.read_excel("Data/Anexo1.NoFetal2019_CE_15-03-23.xlsx", engine="openpyxl")
codigos = pd.read_excel("Data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx", engine="openpyxl",header=8)
divipola = pd.read_excel("Data/Divipola_CE_.xlsx", engine="openpyxl")

print(df.columns.tolist())
print(codigos.columns.tolist())
print(divipola.columns.tolist())

# Preparar datos
codigo_muerte = "COD_MUERTE"
codigo_cie = "Código de la CIE-10 tres caracteres"
codigo_departamento = "COD_DEPARTAMENTO"
codigo_municipio = "COD_MUNICIPIO"

df[codigo_muerte] = df[codigo_muerte].astype(str).str.strip().str.upper()
codigos[codigo_cie] = codigos[codigo_cie].astype(str).str.strip().str.upper()

df[codigo_departamento] = df[codigo_departamento].astype(str).str.strip().str.zfill(2)
divipola[codigo_departamento] = divipola[codigo_departamento].astype(str).str.strip().str.zfill(2)

df[codigo_municipio] = df[codigo_municipio].astype(str).str.strip().str.zfill(3)
divipola[codigo_municipio] = divipola[codigo_municipio].astype(str).str.strip().str.zfill(3)


df = df.merge(codigos, left_on=codigo_muerte, right_on=codigo_cie, how="left", suffixes=("","_cod"))
df = df.merge(divipola, left_on=[codigo_departamento, codigo_municipio], right_on=[codigo_departamento, codigo_municipio], how="left", suffixes=("","_div"))


# Caso 1: DISTRIBUCION DE MUERTES POR DEPARTAMENTO 
dept_col = "DEPARTAMENTO"
ano_col = "AÑO"


df['__anio__'] = pd.to_numeric(df[ano_col], errors='coerce')
df_2019 = df[df['__anio__'] == 2019].copy()

totales_dept = (
    df_2019
    .groupby(dept_col, dropna=False)
    .size()
    .reset_index(name='muertes')
    .sort_values('muertes', ascending=False)
)

print(totales_dept.to_string(index=False))








