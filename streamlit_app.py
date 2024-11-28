import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from streamlit_supabase_config import get_supabase_client
from ws_super import realizar_webscraping
from manual_ingreso import ingreso_manual
from diaria import mostrar_rentabilidad_provida
from dolar import Mindicador
import asyncio
import logging
import nest_asyncio
import plotly.express as px
import streamlit as st

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Permitir que asyncio se reutilice en el entorno de Streamlit
nest_asyncio.apply()

# Configurar la conexión a Supabase
supabase = get_supabase_client()

# Configurar el menú lateral
with st.sidebar:
    selected = option_menu(
        menu_title="AFP Provida",
        options=["Cuota", "Tamaño fondo", "Manual", "Admin"],
        icons=["cash", "bar-chart", "cash", "gear"],
        menu_icon="rocket",
        default_index=0,
    )


# Configuración de las páginas
if selected == "Cuota":
    st.title("Cuota")

    # Botón para ejecutar ws_super y mostrar rentabilidad
    if st.button("Correr proceso"):
        try:
            # Ejecutar el proceso de web scraping
            resultado_ws_super = realizar_webscraping()
            if "success" in resultado_ws_super:
                st.success(f"WS Super: {resultado_ws_super['success']}")
                mostrar_rentabilidad_provida()  # Mostrar la tabla después de ejecutar el proceso
            else:
                st.error(f"WS Super: {resultado_ws_super['error']}")

            # Ejecutar el proceso de Mindicador
            indicador = "dolar"
            api_mindicador = Mindicador(indicador)
            ultimos_dias = api_mindicador.InfoUltimosDias(dias=3)

            if ultimos_dias:
                st.success("Datos del dólar extraídos y guardados correctamente en Supabase.")
            else:
                st.error("No se pudieron extraer o guardar los datos del dólar.")

        except Exception as e:
            st.error(f"Error al ejecutar WS Super: {e}")

elif selected == "Manual":
    ingreso_manual()

elif selected == "Tamano fondo":
    st.title("Tamano fondo")
    st.write("Aquí puedes ver y gestionar el tamaño de los fondos.")
    # Integrar el gráfico de Dash
 

elif selected == "Admin":
    st.title("Admin")
    st.write("Opciones de administración y configuración")

# Nota: Asegúrate de tener configurado el archivo supabase_config.json para que la función get_supabase_client funcione correctamente.
