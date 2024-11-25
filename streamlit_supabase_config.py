import json
from supabase import create_client

def get_supabase_client():
    """
    Crea y devuelve un cliente Supabase utilizando credenciales de un archivo separado.
    """
    with open("supabase_config.json", "r") as file:
        config = json.load(file)
        url = config["url"]
        key = config["key"]
    return create_client(url, key)
