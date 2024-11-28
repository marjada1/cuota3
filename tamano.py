import pandas as pd
import requests
import plotly.express as px
import json
import streamlit as st

def obtener_tamano_fondos():
    # Headers para la solicitud
    headers = {
        "Content-Type": "application/json",
        "apikey": st.secrets["key"],
        "Authorization": f"Bearer {st.secrets['key']}"
    }

    # Endpoint para consultar la tabla tamano_fondos
    url = f"{st.secrets['url']}/rest/v1/tamano_fondos"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Convertir a DataFrame para su manipulación
            df = pd.DataFrame(data)
            print("Datos obtenidos de la tabla tamano_fondos:")
            print(df.head())

            # Eliminar duplicados
            df = df.drop_duplicates()

            # Convertir valor_usd a billones (billions) y redondear a 1 decimal
            df["valor_usd"] = (df["valor_usd"] / 1e6).round(1)
            return df
        else:
            print(f"Error al obtener datos: {response.text}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error de conexión: {str(e)}")
        return pd.DataFrame()

def mostrar_tamano_fondos():
    df = obtener_tamano_fondos()

    if df.empty:
        print("No se encontraron datos en la tabla tamano_fondos.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"])

    # Diagnóstico: verificar AFPs únicas antes de eliminar nulos
    print("AFPs únicas antes de eliminar nulos:", df["afp"].unique())

    # Eliminar filas con valores nulos en valor_usd
    df = df.dropna(subset=["valor_usd"])

    # Diagnóstico: verificar AFPs únicas después de eliminar nulos
    print("AFPs únicas después de eliminar nulos:", df["afp"].unique())

    # Agregar una columna de mes-año para agrupar
    df["mes_anio"] = df["fecha"].dt.to_period("M")

    # Agrupar por mes-año, fondo y afp, y calcular el promedio de valor_usd
    df_resumido = df.groupby(["mes_anio", "fondo", "afp"]).agg({"valor_usd": "mean"}).reset_index()
    df_resumido["mes_anio"] = df_resumido["mes_anio"].dt.to_timestamp()

    # Diagnóstico: verificar AFPs únicas en df_resumido
    print("AFPs únicas en df_resumido:", df_resumido["afp"].unique())
    print("Preview de df_resumido:")
    print(df_resumido.head())

    # Mostrar resumen estadístico por AFP
    print("Resumen estadístico por AFP:")
    resumen_afp = df_resumido.groupby("afp")["valor_usd"].describe()
    print(resumen_afp)

    # Crear gráfico animado de burbujas con colores por AFP y escalas por fondo
    fig = px.scatter(
        df_resumido, x="mes_anio", y="valor_usd", size="valor_usd", color="afp",
        hover_name="fondo", animation_frame="mes_anio", title="Evolución Promedio del Tamaño de Fondo en Billones de USD por AFP y Fondo",
        labels={"valor_usd": "Valor Promedio en Billones de USD", "mes_anio": "Mes", "afp": "AFP", "fondo": "Fondo"},
        size_max=60, height=600, color_discrete_sequence=px.colors.qualitative.Set1
    )

    # Mostrar el gráfico
    fig.show()

if __name__ == "__main__":
    mostrar_tamano_fondos()
