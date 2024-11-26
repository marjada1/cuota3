import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from streamlit_supabase_config import get_supabase_client
from ws_super import realizar_webscraping
from cuprum import fetch_fondos
from manual_ingreso import ingreso_manual
from diaria import mostrar_rentabilidad_provida
import asyncio
import logging
import nest_asyncio

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

# Función para ejecutar fetch_fondos directamente en el bucle de eventos
async def run_fetch_fondos():
    try:
        return await fetch_fondos()
    except Exception as e:
        logging.error(f"Error al ejecutar fetch_fondos: {e}")
        return {"error": str(e)}

# Configuración de las páginas
if selected == "Cuota":
    st.title("Cuota")

    # Botón para ejecutar ws_super y mostrar rentabilidad
    if st.button("Correr proceso WS Super"):
        try:
            resultado_ws_super = realizar_webscraping()
            if "success" in resultado_ws_super:
                st.success(f"WS Super: {resultado_ws_super['success']}")
                mostrar_rentabilidad_provida()  # Mostrar la tabla después de ejecutar el proceso
            else:
                st.error(f"WS Super: {resultado_ws_super['error']}")
        except Exception as e:
            st.error(f"Error al ejecutar WS Super: {e}")

    # Botón para ejecutar fetch_fondos
    if st.button("Correr Cuprum"):
        try:
            resultado_cuprum = asyncio.run(run_fetch_fondos())
            if "error" not in resultado_cuprum:
                st.success(f"Fondos obtenidos: {resultado_cuprum['fondos']}")
            else:
                st.error(f"Cuprum: {resultado_cuprum['error']}")
        except Exception as e:
            st.error(f"Error al ejecutar Cuprum: {e}")

elif selected == "Manual":
    ingreso_manual()

elif selected == "Tamano fondo":
    st.title("Tamano fondo")
    st.write("Aquí puedes ver y gestionar el tamaño de los fondos.")

elif selected == "Admin":
    st.title("Admin")
    st.write("Opciones de administración y configuración.")

# Nota: Asegúrate de tener configurado el archivo supabase_config.json para que la función get_supabase_client funcione correctamente.
