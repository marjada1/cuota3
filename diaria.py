import streamlit as st
import pandas as pd
import requests

# Función genérica para obtener datos desde Supabase
def obtener_rentabilidad(tabla):
    # Headers para la solicitud
    headers = {
        "Content-Type": "application/json",
        "apikey": st.secrets["key"],
        "Authorization": f"Bearer {st.secrets['key']}"
    }

    # Endpoint para consultar la tabla específica
    url = f"{st.secrets['url']}/rest/v1/{tabla}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Convertir a DataFrame para su manipulación
            df = pd.DataFrame(data)
            return df
        else:
            st.error(f"Error al obtener datos de {tabla}: {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error de conexión al obtener {tabla}: {str(e)}")
        return pd.DataFrame()

# Función genérica para transformar los datos
def transformar_rentabilidad(df):
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

def mostrar_rentabilidad(tabla, titulo):
    # Obtener datos
    df = obtener_rentabilidad(tabla)

    if not df.empty:
        # Transformar los datos para el formato deseado
        df_transformado = transformar_rentabilidad(df)

        # Establecer la columna "AFP" como índice
        df_transformado.set_index("AFP", inplace=True)

        # Aplicar estilo para resaltar valores menores a cero con fondo amarillo claro y texto negro
        def resaltar_negativos(val):
            if isinstance(val, (int, float)) and val < 0:
                return 'background-color: #FFFACD; color: black;'  # Fondo amarillo claro, texto negro
            return 'color: black;'  # Asegura que el texto sea negro en todos los casos

        styled_df = df_transformado.style.applymap(resaltar_negativos)

        # Reducir el tamaño de la letra
        styled_df = styled_df.set_properties(**{'font-size': '8pt'})

        # Mostrar la tabla transformada con el índice completo y estilos
        st.write(f"#### {titulo}")
        st.dataframe(styled_df, use_container_width=False)
    else:
        st.error(f"No se encontraron datos en la tabla {tabla}.")




# Mostrar rentabilidades diarias, mensuales y anuales
def main():
    st.title("Rentabilidades AFP Provida")

    # Diaria
    mostrar_rentabilidad("diaria_provida", "Diaria")

    # Mensual
    mostrar_rentabilidad("mensual_provida", "Mensual")

    # Anual
    mostrar_rentabilidad("anual_provida", "Anual")

if __name__ == "__main__":
    main()
