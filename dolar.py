import json
import requests
from datetime import datetime
import streamlit as st

class Mindicador:
    def __init__(self, indicador):
        self.indicador = indicador

    def InfoUltimosDias(self, dias=3):
        """
        Extrae los datos de los últimos 'dias' para el indicador especificado y los guarda en Supabase.
        """
        try:
            url = f'https://mindicador.cl/api/{self.indicador}'
            response = requests.get(url)
            response.raise_for_status()  # Verifica errores HTTP
            data = json.loads(response.text.encode("utf-8"))

            # Filtrar los datos para obtener solo los últimos 'dias'
            valores = data.get("serie", [])[:dias]  # Obtiene las últimas entradas
            if valores:
                print("Estado: Extracción exitosa.")
                data_to_insert = []
                for dia in valores:
                    fecha = dia['fecha'][:10]  # Tomar solo la fecha (YYYY-MM-DD)
                    valor = dia['valor']
                    timestamp = datetime.now().isoformat()  # Timestamp actual
                    print(f"Fecha: {fecha}, Valor: {valor}")

                    # Preparar datos para insertar
                    data_to_insert.append({
                        "fecha": fecha,
                        "dolar": valor,
                        "timestamp": timestamp
                    })

                # Guardar en Supabase (permitir duplicados)
                headers = {
                    "Content-Type": "application/json",
                    "apikey": st.secrets["key"],
                    "Authorization": f"Bearer {st.secrets['key']}"
                }

                for record in data_to_insert:
                    response = requests.post(
                        f"{st.secrets['url']}/rest/v1/dolar",
                        headers=headers,
                        data=json.dumps(record)
                    )

                    if response.status_code in [200, 201]:
                        print(f"Datos guardados correctamente en Supabase para la fecha {record['fecha']}.")
                    elif response.status_code == 409:
                        print(f"Registro duplicado para la fecha {record['fecha']}, se omitió la inserción.")
                    else:
                        print(f"Error al guardar los datos en Supabase: {response.text}")

                return valores
            else:
                print("Estado: No se encontraron datos en la API.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Estado: Error durante la extracción - {e}")
            return None

# Código de prueba
if __name__ == "__main__":
    # Instanciar la clase con un indicador
    indicador = "dolar"  # Cambiar a "uf", "euro", etc., según lo que necesites
    api_mindicador = Mindicador(indicador)

    # Obtener los últimos 3 días de datos y guardarlos en la base de datos
    ultimos_dias = api_mindicador.InfoUltimosDias(dias=3)

    if ultimos_dias:
        print("\nPrueba completada: Datos de los últimos 3 días extraídos y guardados correctamente en Supabase.")
    else:
        print("\nPrueba fallida: No se pudieron extraer o guardar los datos.")
