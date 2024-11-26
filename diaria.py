import streamlit as st
import pandas as pd
import requests

# Función para obtener datos de la tabla "diaria_provida" desde Supabase
def obtener_rentabilidad_provida():
    # Headers para la solicitud
    headers = {
        "Content-Type": "application/json",
        "apikey": st.secrets["key"],
        "Authorization": f"Bearer {st.secrets['key']}"
    }

    # Endpoint para consultar la tabla diaria_provida
    url = f"{st.secrets['url']}/rest/v1/diaria_provida"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Convertir a DataFrame para su manipulación
            df = pd.DataFrame(data)
            return df
        else:
            st.error(f"Error al obtener datos: {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return pd.DataFrame()

def transformar_rentabilidad_provida(df):
    # Verificar que el DataFrame no esté vacío
    if df.empty:
        st.error("El DataFrame está vacío. No se puede transformar.")
        return pd.DataFrame()

    # Pivotar la tabla para que las columnas sean los fondos (A, B, C, D, E)
    df_pivot = df.pivot(index="afp_otra", columns="fondo", values="diferencia_rentabilidad")

    # Renombrar la columna "afp_otra" a "AFP"
    df_pivot.reset_index(inplace=True)
    df_pivot.rename(columns={"afp_otra": "AFP"}, inplace=True)

    return df_pivot

def mostrar_rentabilidad_provida():
    # Obtener datos
    df = obtener_rentabilidad_provida()

    if not df.empty:
        # Transformar los datos para el formato deseado
        df_transformado = transformar_rentabilidad_provida(df)

        # Mostrar la tabla transformada en la aplicación
        st.write("#### Diaria:")
        st.dataframe(df_transformado, use_container_width=True)
    else:
        st.error("No se encontraron datos en la tabla diaria_provida.")
