import streamlit as st
import requests
import yaml
import re
from twilio.rest import Client

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
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        mensaje = f"""
📊 Consulta de IP

🌐 IP: {datos.get('ip')}
📍 País: {datos.get('location', {}).get('country')}
🏙 Ciudad: {datos.get('location', {}).get('city')}
🕒 Zona Horaria: {datos.get('location', {}).get('timezone')}
💻 ISP: {datos.get('isp', {}).get('isp')}
🛡 Riesgo: {datos.get('risk', {}).get('risk_score')}
        """
        client.messages.create(
            body=mensaje.strip(),
            from_=TWILIO_WHATSAPP_NUMBER,
            to=TU_NUMERO_VERIFICADO
        )
        return True
    except Exception as e:
        st.error(f"❌ Error al enviar WhatsApp: {e}")
        return False

# ------------------ UI STREAMLIT ------------------

st.set_page_config(page_title="IP Info App", page_icon="🌍")
st.title("🔍 IPQuery – Enviar resultados a WhatsApp")

if st.button("🌐 Detectar mi IP"):
    ip_auto = obtener_mi_ip()
    if ip_auto:
        st.success(f"Tu IP detectada es: {ip_auto}")
        st.session_state['ip_actual'] = ip_auto
    else:
        st.error("❌ No se pudo detectar tu IP automáticamente.")

ip = st.text_input("🔢 Introduce una IP", st.session_state.get('ip_actual', '1.1.1.1'))

if st.button("📤 Consultar IP y enviar por WhatsApp"):
    if not es_ip_valida(ip):
        st.error("❌ La IP ingresada no es válida.")
    else:
        with st.spinner("Consultando IPQuery..."):
            datos = consultar_datos_ip(ip)
            if datos:
                st.success("✅ Consulta exitosa")

                st.subheader("📍 Ubicación")
                st.write(datos.get("location"))

                st.subheader("🌐 ISP")
                st.write(datos.get("isp"))

                st.subheader("🔐 Riesgo")
                st.write(datos.get("risk"))

                enviado = enviar_whatsapp(datos)
                if enviado:
                    st.success("📬 Resultado enviado a tu WhatsApp (sandbox)")
            else:
                st.error("❌ No se pudo obtener los datos de esa IP.")
