import streamlit as st
import requests
from auth_helpers import get_backend_url, auth_headers

st.set_page_config(page_title="DEBUG Sesión y Backend", layout="centered")

BACKEND_URL = get_backend_url()

st.markdown("## 🔍 DEBUG Sesión y Backend")

st.write("### 1) BACKEND_URL que ve Streamlit:")
st.code(BACKEND_URL, language="bash")

st.write("### 2) session_state actual:")
st.json(st.session_state)

st.write("### 3) Probar /auth/login (si querés)")
email = st.text_input("Email de prueba", "login_test@mktlab.com")
pwd = st.text_input("Password", "Test123!", type="password")

if st.button("Probar login backend"):
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": pwd},
            timeout=15
        )
        st.write("Status code:", r.status_code)
        st.write("Respuesta JSON:")
        st.json(r.json())
    except Exception as e:
        st.error(f"Error llamando al backend: {e}")

st.write("### 4) Probar endpoint protegido (si ya tenés token)")
if st.button("Probar /users/mi-usuario (ejemplo)"):
    try:
        r = requests.get(
            f"{BACKEND_URL}/users",
            headers=auth_headers(),
            timeout=15
        )
        st.write("Status code:", r.status_code)
        st.write("Respuesta cruda:", r.text)
    except Exception as e:
        st.error(f"Error llamando al backend (users): {e}")
