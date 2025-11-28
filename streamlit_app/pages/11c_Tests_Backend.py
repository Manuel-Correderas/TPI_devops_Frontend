# streamlit_app/pages/11c_🔧_Tests_Backend.py

import os
import subprocess
from pathlib import Path

import streamlit as st
from auth_helpers import require_admin  # o require_login si querés abrirlo más


st.set_page_config(
    page_title="🔧 Tests Backend - Ecom MKT Lab",
    layout="wide",
    page_icon="🧪",
)

# =========================
# Solo ADMIN (opcional)
# =========================
try:
    require_admin()
except Exception:
    st.stop()

# =========================
# Paths del proyecto
# =========================
REPO_ROOT = Path(__file__).resolve().parents[1]   # raíz del repo (donde está backend/ y tests/)
TESTS_DIR = REPO_ROOT / "tests"

st.title("🔧 Ejecutor de tests del backend")
st.write(
    """
Esta página ejecuta los **tests de backend** usando `pytest` contra la base de datos
de testing (SQLite), igual que si corrieras:

`pytest -q`

> Pensado para entorno local. En Render/producción puede no tener acceso a pytest.
"""
)

st.markdown("---")
st.caption(f"📂 Raíz del repo detectada: `{REPO_ROOT}`")
st.caption(f"🧪 Carpeta de tests: `{TESTS_DIR}`")

if not TESTS_DIR.exists():
    st.error("❌ No se encontró la carpeta `tests/` en la raíz del proyecto.")
    st.stop()

if "tests_running" not in st.session_state:
    st.session_state["tests_running"] = False

run = st.button(
    "▶️ Ejecutar todos los tests de backend",
    type="primary",
    disabled=st.session_state["tests_running"],
)

if run:
    st.session_state["tests_running"] = True
    st.info("⏳ Ejecutando `pytest -q`...")

    cmd = ["pytest", "-q"]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )

        st.session_state["tests_running"] = False

        st.subheader("📜 Salida de pytest")
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        if not output.strip():
            output = "Sin salida de pytest (stdout/stderr vacíos)."

        st.code(output, language="bash")

        if result.returncode == 0:
            st.success("✅ Todos los tests pasaron correctamente (exit code 0).")
        else:
            st.error(f"❌ Algunos tests fallaron (exit code {result.returncode}).")

    except FileNotFoundError:
        st.session_state["tests_running"] = False
        st.error(
            "❌ No se pudo ejecutar `pytest`. "
            "Verificá que esté instalado en tu entorno virtual (`pip install pytest`)."
        )
    except Exception as e:
        st.session_state["tests_running"] = False
        st.error(f"❌ Error inesperado al ejecutar tests: {e}")
