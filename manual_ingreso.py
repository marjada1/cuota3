import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# Configurar las opciones predefinidas
afp_options = ["MODELO", "PROVIDA", "CAPITAL", "UNO", "HABITAT", "CUPRUM", "PLANVITAL"]
fondo_options = ["A", "B", "C", "D", "E"]

def ingreso_manual():
    st.title("Ingreso Manual de Cuotas")

    # Selección de AFP
    afp = st.selectbox("Selecciona la AFP", afp_options)

    # Selección de Fondo
    fondo = st.selectbox("Selecciona el Fondo", fondo_options)

    # Fecha (por defecto el día de ayer)
    ayer = datetime.today() - timedelta(days=1)
    fecha = st.date_input("Fecha", value=ayer, max_value=ayer)

    # Valor de Cuota
    valor_cuota = st.text_input("Valor Cuota", value="0,0000", help="Ingresa el valor de la cuota (e.g., 1234,5678)")

    # Botón de enviar
    if st.button("Agregar Cuota"):
        try:
            # Validaciones
            valor_cuota_parsed = float(valor_cuota.replace(",", "."))
            if valor_cuota_parsed <= 1000:
                st.error("El valor de la cuota debe ser mayor a 1000.")
                return

            # Enviar datos a Supabase
            data = {
                "afp": afp,
                "fondo": fondo,
                "fecha": fecha.isoformat(),
                "valor_cuota": valor_cuota_parsed,
                "hora_de_agregacion": datetime.now().isoformat(),
                "fuente": "Manual",
            }

            headers = {
                "Content-Type": "application/json",
                "apikey": st.secrets["key"],
                "Authorization": f"Bearer {st.secrets['key']}"
            }

            response = requests.post(
                f"{st.secrets['url']}/rest/v1/manual",
                headers=headers,
                data=json.dumps(data)
            )

            if response.status_code in [200, 201]:
                st.success("Cuota ingresada con éxito.")
                # Mostrar serpentinas de celebración con Streamlit
                st.balloons()
            else:
                st.error(f"Error al guardar los datos: {response.text}")

        except ValueError:
            st.error("Por favor, ingresa un valor de cuota válido.")
        except Exception as e:
            st.error(f"Error al guardar los datos: {str(e)}")
