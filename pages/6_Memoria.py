import streamlit as st
from modules.memory import MemoryManager
from modules.stats import StatsManager
from modules.bosses import BossManager
from modules.world import WorldManager
import os

st.set_page_config(
    page_title="Memoria — Aureon Nightweaver",
    layout="wide"
)

memory = MemoryManager()
stats = StatsManager()
boss = BossManager()
world = WorldManager()

BACKUP_DIR = "data/backups/"

# -----------------------------------------------------------
# TÍTULO PRINCIPAL
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#A8C0FF;'>🗃️ Archivo de Memoria</h1>
    <h3 style='color:#7F8CFF; margin-top:-10px;'>
        El Archivo del Tiempo de Aureon Nightweaver
    </h3>
    """,
    unsafe_allow_html=True
)

st.markdown("Aquí puedes ver todos tus backups diarios y restaurar el sistema a un estado anterior.")

# -----------------------------------------------------------
# LISTA DE BACKUPS
# -----------------------------------------------------------
st.markdown("## 📅 Backups Disponibles")

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

files = sorted(os.listdir(BACKUP_DIR))

if not files:
    st.info("No hay backups disponibles todavía.")
else:
    for f in files:
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#1d1d2d; padding:10px; margin-bottom:10px; border-radius:8px;">
                    <b style="color:#A8C0FF;">{f}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            # ---------------------------------------------------
            # Botón restaurar backup
            # ---------------------------------------------------
            with col1:
                if st.button(f"🔄 Restaurar {f}"):
                    memory.restore_backup(f)
                    st.success(f"Sistema restaurado al estado de {f}.")
                    st.experimental_rerun()

            # ---------------------------------------------------
            # Exportar capítulo desde este backup
            # ---------------------------------------------------
            with col2:
                if st.button(f"📘 Exportar capítulo", key=f"chapter_{f}"):
                    date = f.replace(".json", "")
                    chapter = memory.export_day_as_chapter(date)
                    st.text_area(f"Capítulo {date}", chapter, height=350)

            # ---------------------------------------------------
            # Eliminar backup (opcional)
            # ---------------------------------------------------
            with col3:
                if st.button(f"🗑 Eliminar", key=f"delete_{f}"):
                    os.remove(BACKUP_DIR + f)
                    st.warning(f"Backup {f} eliminado.")
                    st.experimental_rerun()

# -----------------------------------------------------------
# CREAR BACKUP MANUAL
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ➕ Crear Backup Manual")

name = st.text_input("Nombre del backup (sin espacios):")

if st.button("Crear Backup Manual"):
    if name.strip() == "":
        st.error("Escribe un nombre válido.")
    else:
        r = memory.manual_backup(name)
        st.success(r)
        st.experimental_rerun()

# -----------------------------------------------------------
# BACKUP DEL DÍA
# -----------------------------------------------------------
st.markdown("---")
if st.button("📦 Crear Backup Automático de Hoy"):
    r = memory.auto_backup()
    st.success(r)
