import streamlit as st
import requests
import yaml
import re
from twilio.rest import Client
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import pandas as pd

# ------------------ TWILIO SANDBOX ------------------
TWILIO_SID = "AC665d269ec686f198790de0fae15ac484"
TWILIO_AUTH_TOKEN = "4f017448a69c340bc4ff6e221b06a2fa"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Número fijo del sandbox
TU_NUMERO_VERIFICADO = "whatsapp:+51986420272"   # Tu número de celular, con prefijo internacional

# ------------------ FUNCIONES ------------------

def es_ip_valida(ip):
    patron = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(patron, ip):
        return False
    partes = ip.split(".")
    return all(0 <= int(p) <= 255 for p in partes)

def obtener_mi_ip():
    try:
        r = requests.get("https://api.ipquery.io/")
        return r.text.strip()
    except:
        return None

def consultar_datos_ip(ip):
    url = f"https://api.ipquery.io/{ip}?format=yaml"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = yaml.safe_load(resp.text)
            data["ip"] = ip
            return data
    except Exception as e:
        st.error(f"❌ Error al consultar la API: {e}")
    return None

def enviar_whatsapp(datos):
   mapa = f"https://www.google.com/maps?q={datos['lat']},{datos['lon']}"

mensaje = f"""
📍 Ubicación GPS:
Lat: {datos['lat']}, Lon: {datos['lon']}

🌐 IP: {datos.get('ip')}
🏙 Ciudad: {datos.get('location', {}).get('city')}
🌍 País: {datos.get('location', {}).get('country')}
💻 ISP: {datos.get('isp', {}).get('isp')}
🗺️ Mapa: {mapa}
"""


# ------------------ UI STREAMLIT ------------------

st.set_page_config(page_title="GeoIP Tracker", page_icon="🌍")
st.title("🌐 IP + 📍 Geolocalización Real + WhatsApp")

# Obtener ubicación GPS del navegador
from streamlit_js_eval import streamlit_js_eval, get_geolocation

coords = streamlit_js_eval(label="Obtener ubicación", value=get_geolocation(), key="get_location")

if coords and coords.get("coords"):
    lat = coords["coords"]["latitude"]
    lon = coords["coords"]["longitude"]
    st.success("📍 Ubicación GPS obtenida exitosamente")
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
else:
    st.warning("🔒 Permite la ubicación en el navegador para obtener coordenadas reales.")


# Obtener IP del usuario
ip_actual = obtener_mi_ip()
ip = st.text_input("🔢 Tu IP detectada (editable):", ip_actual or "1.1.1.1")

if st.button("📤 Consultar IP + Enviar por WhatsApp"):
    if not es_ip_valida(ip):
        st.error("❌ IP inválida.")
    else:
        datos = consultar_datos_ip(ip)
        if datos:
            st.subheader("📍 IPQuery Ubicación")
            st.write(datos.get("location"))

            st.subheader("🌐 ISP")
            st.write(datos.get("isp"))

            st.subheader("🔐 Riesgo")
            st.write(datos.get("risk"))

            if coords and coords.get("coords"):
                datos['lat'] = lat
                datos['lon'] = lon

            enviado = enviar_whatsapp(datos)
            if enviado:
                st.success("✅ Información enviada por WhatsApp.")


