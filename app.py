import streamlit as st
import requests
import yaml
import re
import pandas as pd
from twilio.rest import Client
from streamlit_js_eval import streamlit_js_eval, get_geolocation

# ------------------ TWILIO SANDBOX CONFIG ------------------
TWILIO_SID = "AC665d269ec686f198790de0fae15ac484"
TWILIO_AUTH_TOKEN = "4f017448a69c340bc4ff6e221b06a2fa"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Número fijo del sandbox
TU_NUMERO_VERIFICADO = "whatsapp:+51986420272"   # Tu número de celular, con prefijo internacional

# ------------------ FUNCIONES AUXILIARES ------------------

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
        st.error(f"❌ Error al consultar IPQuery: {e}")
    return None

def enviar_whatsapp(datos):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        lat = datos.get("lat")
        lon = datos.get("lon")
        mapa = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "Ubicación no disponible"

        mensaje = f"""
📍 Ubicación GPS:
Lat: {lat or 'N/D'}, Lon: {lon or 'N/D'}

🌐 IP: {datos.get('ip')}
🏙 Ciudad: {datos.get('location', {}).get('city')}
🌍 País: {datos.get('location', {}).get('country')}
💻 ISP: {datos.get('isp', {}).get('isp')}
🗺️ Mapa: {mapa}
        """
        client.messages.create(
            body=mensaje.strip(),
            from_=TWILIO_WHATSAPP_NUMBER,
            to=TU_NUMERO_VERIFICADO
        )
        return True
    except Exception as e:
        st.error(f"❌ Error al enviar mensaje por WhatsApp: {e}")
        return False

# ------------------ UI PRINCIPAL ------------------

st.set_page_config(page_title="GeoIP App", page_icon="🌍")
st.title("🌍 Geolocalización + IP + WhatsApp")

# 1. Geolocalización real
coords = streamlit_js_eval(label="Obtener ubicación", value=get_geolocation(), key="get_location")

if coords and coords.get("coords"):
    lat = coords["coords"]["latitude"]
    lon = coords["coords"]["longitude"]
    st.success("📍 Ubicación GPS obtenida correctamente")
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
else:
    st.warning("🔒 No se pudo obtener la ubicación GPS. Asegúrate de permitir acceso en el navegador.")
    lat, lon = None, None

# 2. IP del usuario
ip_detectada = obtener_mi_ip()
ip = st.text_input("🔢 Tu IP detectada (editable):", ip_detectada or "1.1.1.1")

# 3. Botón de consulta
if st.button("📤 Consultar y enviar por WhatsApp"):
    if not es_ip_valida(ip):
        st.error("❌ La IP ingresada no es válida.")
    else:
        with st.spinner("Consultando datos..."):
            datos = consultar_datos_ip(ip)
            if datos:
                datos["lat"] = lat
                datos["lon"] = lon

                st.subheader("📍 IPQuery Ubicación")
                st.write(datos.get("location"))

                st.subheader("🌐 ISP")
                st.write(datos.get("isp"))

                st.subheader("🔐 Riesgo")
                st.write(datos.get("risk"))

                # Mapa de IP
                ip_lat = datos.get("location", {}).get("latitude")
                ip_lon = datos.get("location", {}).get("longitude")
                if ip_lat and ip_lon:
                    mapa_url = f"https://www.google.com/maps?q={ip_lat},{ip_lon}"
                    st.markdown(f"[🗺️ Ver ubicación IP en Google Maps]({mapa_url})", unsafe_allow_html=True)

                if enviar_whatsapp(datos):
                    st.success("✅ Información enviada a WhatsApp correctamente.")
