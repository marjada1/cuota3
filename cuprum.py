import nest_asyncio
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import json
import uuid
import requests
import logging
from datetime import datetime
import streamlit as st
import ssl

# Aplicar nest_asyncio para permitir ejecución de bucles asincrónicos
nest_asyncio.apply()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Deshabilitar verificación de certificados SSL
ssl._create_default_https_context = ssl._create_unverified_context

async def fetch_fondos():
    """
    Realiza web scraping en el sitio de Cuprum para obtener valores de fondos.
    
    Returns:
        dict: Diccionario con los fondos o un mensaje de error
    """
    logging.info("Iniciando el proceso de web scraping para Cuprum...")
    
    # Crear sesión HTML asíncrona
    session = AsyncHTMLSession()
    
    data = []
    
    try:
        # URL del sitio web de Cuprum
        url = "https://www6.cuprum.cl/multifondos/que-es-la-rentabilidad-y-el-valor-cuota"
        
        # Realizar el scraping
        response = await session.get(url)
        
        # Renderizar JavaScript
        await response.html.arender(timeout=30)
        
        # Parsear el HTML
        soup = BeautifulSoup(response.html.html, 'html.parser')
        
        # Extraer datos de los fondos
        fondos = {}
        for span in soup.find_all('span', id=lambda x: x and x.startswith('valor-cuota-')):
            nombre_fondo = span['id'].replace('valor-cuota-', '').upper()
            valor_cuota = span.text.strip().replace("$", "").replace(",", ".").strip()
            fondos[nombre_fondo] = valor_cuota
        
        # Extraer y guardar la fecha como texto
        fecha_actualizacion_span = soup.find('span', id="valor-cuota-fecha-actualizacion")
        fecha_actualizacion = fecha_actualizacion_span.text.strip() if fecha_actualizacion_span else "Fecha no encontrada"
        
        try:
            fecha_dt = datetime.strptime(fecha_actualizacion, "%d/%m/%Y")
            fecha_actualizacion_formateada = fecha_dt.strftime("%Y-%m-%d")
        except ValueError:
            logging.warning(f"Formato de fecha inválido: {fecha_actualizacion}")
            fecha_actualizacion_formateada = None
        
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Construir los datos para Supabase
        for fondo, valor_cuota in fondos.items():
            data.append({
                "id": str(uuid.uuid4()),
                "afp": "CUPRUM",
                "fondo": fondo,
                "fecha": fecha_actualizacion_formateada,
                "valor_cuota": valor_cuota,
                "hora_de_agregacion": hora_actual,
                "fuente": "Web Scraping Cuprum"
            })
        
        # Imprimir datos para verificación
        logging.info(f"Datos obtenidos del scraping: {json.dumps(data, indent=4)}")
    
    except Exception as e:
        logging.error(f"Error durante el scraping: {e}")
        return {"error": str(e)}
    
    finally:
        await session.close()
    
    if not data:
        logging.error("No se obtuvieron datos válidos del web scraping.")
        return {"error": "No se pudieron obtener datos de los fondos"}
    
    # Configuración de Supabase
    headers = {
        "Content-Type": "application/json",
        "apikey": st.secrets["key"],
        "Authorization": f"Bearer {st.secrets['key']}"
    }
    
    # Enviar los datos a Supabase
    try:
        response = requests.post(
            f"{st.secrets['url']}/rest/v1/cuprum",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code in [200, 201]:
            logging.info("Datos enviados correctamente a Supabase.")
            return {"success": "Datos guardados correctamente en Supabase"}
        else:
            logging.error(f"Error al enviar los datos a Supabase: {response.text}")
            return {"error": f"No se pudieron guardar los datos: {response.text}"}
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al enviar datos a Supabase: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Importar asyncio para ejecutar la función asíncrona
    import asyncio
    
    # Ejecutar la función asíncrona
    resultado = asyncio.run(fetch_fondos())
    logging.info(f"Resultado final: {resultado}")