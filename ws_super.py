import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import uuid
import math

# Función para dividir la lista de datos en lotes pequeños
def dividir_en_lotes(lista, tamaño_lote):
    for i in range(0, len(lista), tamaño_lote):
        yield lista[i:i + tamaño_lote]

def realizar_webscraping():
    print("Iniciando el proceso de web scraping...")
    urls_fondos = {
        'A': 'https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php?tf=A',
        'B': 'https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php?tf=B',
        'C': 'https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php?tf=C',
        'D': 'https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php?tf=D',
        'E': 'https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php?tf=E'
    }

    meses = {
        "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
        "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
        "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
    }

    data = []

    for fondo, url in urls_fondos.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table', class_='table table-striped table-hover table-bordered table-condensed')
                if len(tables) > 1:
                    date_table = tables[1]
                    center_tag = date_table.find('center')
                    if center_tag:
                        date_text = center_tag.text.strip().split()[0]
                        dia, mes_texto, anio = date_text.split("-")
                        mes = meses.get(mes_texto, "01")
                        fecha_actualizacion_formateada = f"{anio}-{mes}-{dia.zfill(2)}"
                    else:
                        print(f"No se encontró fecha para el fondo {fondo}")
                        continue

                    rows = date_table.find_all('tr')[2:]
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) == 3:
                            afp = columns[0].text.strip()
                            valor_cuota = columns[1].text.strip().replace(".", "").replace(",", ".")
                            valor_patrimonio = columns[2].text.strip().replace(",", ".")

                            if valor_cuota == "(*)" or valor_patrimonio == "(*)":
                                print(f"Omitiendo datos inválidos para AFP: {afp}, Fondo: {fondo}")
                                continue

                            hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            data.append({
                                "id": str(uuid.uuid4()),
                                "afp": afp,
                                "fondo": fondo,
                                "fecha": fecha_actualizacion_formateada,
                                "valor_cuota": valor_cuota,
                                "valor_patrimonio": valor_patrimonio,
                                "timestamp": hora_actual,
                                "fuente": "Web Scraping"
                            })
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos del fondo {fondo}: {e}")

    if not data:
        return {"error": "No se pudieron obtener datos de los fondos"}

    # Enviar datos en lotes pequeños
    tamaño_lote = 50  # Ajusta este valor según las limitaciones del servidor
    headers = {
        "Content-Type": "application/json",
        "apikey": st.secrets["key"],
        "Authorization": f"Bearer {st.secrets['key']}"
    }

    for lote in dividir_en_lotes(data, tamaño_lote):
        try:
            response = requests.post(
                f"{st.secrets['url']}/rest/v1/fondos",
                headers=headers,
                data=json.dumps(lote)
            )
            if response.status_code in [200, 201]:
                print(f"Lote de {len(lote)} datos guardado correctamente.")
            else:
                print(f"Error al guardar el lote: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar lote: {e}")

    return {"success": "Proceso de carga completado en lotes."}

if __name__ == "__main__":
    resultado = realizar_webscraping()
    print(resultado)
