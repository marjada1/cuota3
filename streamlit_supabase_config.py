import streamlit as st
from supabase import create_client

def get_supabase_client():
    """
    Crea y devuelve un cliente Supabase utilizando secrets de Streamlit.
    """
    url = st.secrets["url"]
    key = st.secrets["key"]
    return create_client(url, key)
