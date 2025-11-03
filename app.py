import pandas as pd
import plotly.express as px
import numpy as np
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
dept_col = "DEPARTAMENTO"
ano_col = "AÑO"
manera_muerte= "MANERA_MUERTE"
ciudad_col = "MUNICIPIO"
mes_col = "MES"

df[codigo_muerte] = df[codigo_muerte].astype(str).str.strip().str.upper()
codigos[codigo_cie] = codigos[codigo_cie].astype(str).str.strip().str.upper()

df[codigo_departamento] = df[codigo_departamento].astype(str).str.strip().str.zfill(2)
divipola[codigo_departamento] = divipola[codigo_departamento].astype(str).str.strip().str.zfill(2)

df[codigo_municipio] = df[codigo_municipio].astype(str).str.strip().str.zfill(3)
divipola[codigo_municipio] = divipola[codigo_municipio].astype(str).str.strip().str.zfill(3)


df = df.merge(codigos, left_on=codigo_muerte, right_on=codigo_cie, how="left", suffixes=("","_cod"))
df = df.merge(divipola, left_on=[codigo_departamento, codigo_municipio], right_on=[codigo_departamento, codigo_municipio], how="left", suffixes=("","_div"))


# Caso 1: DISTRIBUCION DE MUERTES POR DEPARTAMENTO 

df['__anio__'] = pd.to_numeric(df[ano_col], errors='coerce')
df_2019 = df[df['__anio__'] == 2019].copy()

totales_dept = (
    df_2019
    .groupby(dept_col, dropna=False)
    .size()
    .reset_index(name='muertes')
    .sort_values('muertes', ascending=False)
)

#print(totales_dept.to_string(index=False))

# Caso 2: DISTRIBUCION DE MUERTES POR MES


totales_mes = (
    df_2019
    .groupby(mes_col, dropna=False)
    .size()
    .reset_index(name='muertes')
    .sort_values('muertes', ascending=False)
)

meses_dict = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

totales_mes[mes_col] = totales_mes[mes_col].map(meses_dict)

orden_meses = list(meses_dict.values())
totales_mes[mes_col] = pd.Categorical(totales_mes[mes_col], categories=orden_meses, ordered=True)
totales_mes = totales_mes.sort_values(mes_col)

#print(totales_mes.to_string(index=False))

# Caso 3: TOP HOMICIDIOS POR CIUDAD

df_homicidios = df[df[manera_muerte].astype(str).str.strip().str.lower() == 'homicidio']

top_homicidios = (
    df_homicidios
    .groupby(ciudad_col, dropna=False)
    .size()
    .reset_index(name='muertes')
    .sort_values('muertes', ascending=False)
    .head(5)
)

# print(top_homicidios.to_string(index=False))


# Caso 4: CIUDADES CON MENOS MUERTES

top_menos_mortandad = (
    df_2019
    .groupby(ciudad_col, dropna=False)
    .size()
    .reset_index(name='muertes')
    .sort_values('muertes', ascending=True)
    .head(10)
)

#print(top_menos_mortandad.to_string(index=False))


# Caso 5: PRINCIPALES CAUSAS DE MUERTE

top_causas = (
    df_2019
    .groupby(["MANERA_MUERTE", "COD_MUERTE"], dropna=False)
    .size()
    .reset_index(name="muertes")
    .sort_values("muertes", ascending=False)
    .head(10)
)

top_causas = top_causas.merge(codigos,left_on="COD_MUERTE",right_on="Código de la CIE-10 cuatro caracteres",how="left")

top_causas = top_causas[[
    "MANERA_MUERTE",
    "COD_MUERTE",
    "muertes",
    "Descripcion  de códigos mortalidad a cuatro caracteres"
]]

#print(top_causas.to_string(index=False))


# Caso 6: MUERTES POR DEPARTAMENTO Y SEXO (alternativa 4: detalle por departamento)

dept_sexo = (
    df_2019
    .groupby([dept_col, "SEXO"], dropna=False)
    .size()
    .reset_index(name="muertes")
    .sort_values(by=[dept_col, "SEXO"])
)

print(dept_sexo.to_string(index=False))

detalle = (
    dept_sexo
    .groupby(dept_col)
    .apply(lambda g: g[["SEXO", "muertes"]].to_dict(orient="records"))
    .reset_index(name="detalle")
)

totales = (
    dept_sexo
    .groupby(dept_col)["muertes"]
    .sum()
    .reset_index(name="total")
)

print(detalle.to_string(index=False))
print(totales.to_string(index=False))


# Caso 7: DISTRIBUCION DE MUERTES POR GRUPOS DE EDAD

df_edades = df_2019.copy()
df_edades["GRUPO_EDAD1"] = pd.to_numeric(df_edades["GRUPO_EDAD1"], errors="coerce")

condiciones = [
    df_edades["GRUPO_EDAD1"].between(0, 4, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(5, 6, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(7, 8, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(9, 10, inclusive="both"),
    df_edades["GRUPO_EDAD1"] == 11,
    df_edades["GRUPO_EDAD1"].between(12, 13, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(14, 16, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(17, 19, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(20, 24, inclusive="both"),
    df_edades["GRUPO_EDAD1"].between(25, 28, inclusive="both"),
    df_edades["GRUPO_EDAD1"] == 29
]

categorias = [
    "Mortalidad neonatal",
    "Mortalidad infantil",
    "Primera infancia",
    "Niñez",
    "Adolescencia",
    "Juventud",
    "Adultez temprana",
    "Adultez intermedia",
    "Vejez",
    "Longevidad / Centenarios",
    "Edad desconocida"
]

rangos = [
    "Menor de 1 mes",
    "1 a 11 meses",
    "1 a 4 años",
    "5 a 14 años",
    "15 a 19 años",
    "20 a 29 años",
    "30 a 44 años",
    "45 a 59 años",
    "60 a 84 años",
    "85 a 100+ años",
    "Sin información"
]

df_edades["CATEGORIA_EDAD"] = np.select(condiciones, categorias, default="Sin información")

totales_por_categoria = (
    df_edades
    .groupby("CATEGORIA_EDAD")
    .size()
    .reset_index(name="total_muertes")
    .sort_values("total_muertes", ascending=False)
)

#print(totales_por_categoria.to_string(index=False))










