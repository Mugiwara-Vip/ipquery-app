import streamlit as st
import requests
import yaml

st.set_page_config(page_title="IP Info App", page_icon="🌍")
st.success("✅ La app se cargó correctamente")

st.title("🔍 IPQuery – Enriquecimiento de IP")
ip = st.text_input("Introduce una IP para consultar", "1.1.1.1")

if st.button("Consultar IP"):
    with st.spinner("Consultando IPQuery..."):
        url = f"https://api.ipquery.io/{ip}?format=yaml"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = yaml.safe_load(resp.text)
                st.subheader("📍 Ubicación")
                st.write(data.get("location"))

                st.subheader("🌐 ISP")
                st.write(data.get("isp"))

                st.subheader("🔐 Riesgo")
                st.write(data.get("risk"))
            else:
                st.error("No se pudo consultar la IP.")
        except Exception as e:
            st.error(f"Error al consultar la API: {e}")
