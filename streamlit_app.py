import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from streamlit_supabase_config import get_supabase_client

# Configurar la conexión a Supabase
supabase = get_supabase_client()

# Configurar el menú lateral
with st.sidebar:
    selected = option_menu(
        menu_title="AFP Provida",
        options=["Tamano fondo", "Cuota", "Admin"],
        icons=["bar-chart", "cash", "gear"],
        menu_icon="rocket",
        default_index=1,
    )

# Configuración de las páginas

if selected == "Cuota":
    st.title("Cuota")
    st.button("Correr proceso")

elif selected == "Tamano fondo":
    st.title("Tamano fondo")
    st.write("Aquí puedes ver y gestionar el tamaño de los fondos.")

elif selected == "Admin":
    st.title("Admin")
    st.write("Opciones de administración y configuración.")

# Nota: Asegúrate de tener configurado el archivo supabase_config.json para que la función get_supabase_client funcione correctamente.
