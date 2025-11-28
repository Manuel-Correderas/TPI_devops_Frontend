# streamlit_app/auth_helpers.py
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ============================
# BACKEND URL
# ============================
def get_backend_url() -> str:
    """
    Devuelve la URL base del backend.
    - Usa BACKEND_URL del entorno si existe (por ej. la de Render)
    - Si no, cae a localhost para desarrollo.
    """
    url = os.getenv("BACKEND_URL")
    if url:
        return url.rstrip("/")  # sacamos / final si lo hubiera
    return "http://127.0.0.1:8000"


# ============================
# SESSION AUTH
# ============================
def set_auth_session(data: dict) -> None:
    """
    Normaliza la respuesta del backend y la guarda en session_state.

    Esperado para /auth/login ahora:
    {
        "ok": True,
        "access_token": "...",
        "token_type": "bearer",
        "user": {
            "id": "...",
            "email": "...",
            "roles": ["COMPRADOR", "VENDEDOR", "ADMIN"],
            "premium": 0,
            "dni_bloqueado": 0
        }
    }
    """
    if not isinstance(data, dict):
        return

    # ---- Token ----
    token = data.get("access_token") or data.get("token") or data.get("jwt")
    if token:
        st.session_state["auth_token"] = token

    # ---- Usuario ----
    user = data.get("user")
    if not isinstance(user, dict):
        # fallback si el backend algún día devuelve todo plano
        user = data if isinstance(data, dict) else {}

    # premium (int, default 0)
    premium_val = user.get("premium", data.get("premium", 0))
    try:
        premium_val = int(premium_val or 0)
    except Exception:
        premium_val = 0

    user["premium"] = premium_val
    st.session_state["premium"] = premium_val

    # dni_bloqueado opcional (por si lo querés usar después)
    dni_block = user.get("dni_bloqueado", data.get("dni_bloqueado", 0))
    try:
        dni_block = int(dni_block or 0)
    except Exception:
        dni_block = 0
    user["dni_bloqueado"] = dni_block
    st.session_state["dni_bloqueado"] = dni_block

    # ---- Roles ----
    roles_raw = (
        user.get("roles")
        or user.get("role")
        or data.get("roles")
        or []
    )

    if isinstance(roles_raw, str):
        roles_raw = [roles_raw]

    roles: list[str] = []
    for r in roles_raw:
        if isinstance(r, dict):
            name = (
                r.get("name")
                or r.get("role")
                or r.get("code")
                or r.get("codigo")
            )
            if name:
                roles.append(str(name).upper())
        else:
            roles.append(str(r).upper())

    st.session_state["roles"] = roles
    st.session_state["auth_roles"] = roles
    st.session_state["is_admin"] = "ADMIN" in roles

    # ---- IDs / nombre / email ----
    uid = (
        user.get("id")
        or user.get("user_id")
        or data.get("user_id")
        or data.get("id")
    )
    if uid:
        st.session_state["auth_user_id"] = uid

    st.session_state["auth_user_name"] = user.get("nombre") or user.get("email")
    st.session_state["auth_user_email"] = user.get("email")

    # Guardamos el objeto user completo al final
    st.session_state["user"] = user


# ============================
# HELPERS COMPARTIDOS
# ============================
def auth_headers() -> dict:
    """
    Headers con Authorization para requests al backend.
    """
    tok = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def require_login():
    """
    Corta la ejecución de la página si no hay sesión iniciada.
    """
    if "auth_token" not in st.session_state:
        st.warning("Tenés que iniciar sesión.")
        # ⚠️ AJUSTÁ el nombre del archivo si tu login se llama distinto
        st.page_link("pages/0_🔐_Login.py", label="Ir a Login", icon="🔐")
        st.stop()


def require_admin():
    """
    Solo deja pasar a usuarios con rol ADMIN.
    """
    require_login()
    roles = [str(r).upper() for r in st.session_state.get("roles", [])]
    if "ADMIN" not in roles:
        st.error("No tenés permisos para acceder a este panel.")
        st.stop()
