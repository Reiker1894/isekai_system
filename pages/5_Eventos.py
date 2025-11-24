import streamlit as st
from modules.world import WorldManager
from modules.stats import StatsManager
from modules.memory import MemoryManager
from datetime import datetime

st.set_page_config(
    page_title="Eventos — Aureon Nightweaver",
    layout="wide"
)

world = WorldManager()
stats = StatsManager()
memory = MemoryManager()

events = world.data.get("events", [])

# -----------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#A8C0FF;'>📜 Registro de Eventos</h1>
    <h3 style='color:#7F8CFF; margin-top:-10px;'>
        Historia viva de Aureon Nightweaver
    </h3>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------
# FILTRO DE EVENTOS
# -----------------------------------------------------------
st.markdown("## 🔍 Filtrar Eventos")

categories = ["Todos", "real_event", "random_world"]

selected = st.radio("Elige categoría:", categories, horizontal=True)

if selected == "Todos":
    filtered_events = events
else:
    filtered_events = [e for e in events if e["type"] == selected]

# -----------------------------------------------------------
# MOSTRAR EVENTOS
# -----------------------------------------------------------
st.markdown("## 🗂️ Eventos Registrados")

if not filtered_events:
    st.info("No hay eventos para mostrar.")
else:
    for i, e in enumerate(filtered_events[::-1]):  # reverse chronological
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#1b1b2b; padding:15px; border-radius:8px; margin-bottom:12px;">
                    <b style="color:#A8C0FF;">{e.get('type').upper()}</b><br>
                    <span style="color:#9FA7FF;">{e.get('date')}</span><br><br>
                    <i style="color:white;">{e.get('description', e.get('name',''))}</i>
                </div>
                """,
                unsafe_allow_html=True
            )

            # BOTÓN PARA BORRAR EVENTO INDIVIDUAL
            if st.button(f"Eliminar evento #{i}", key=f"delete_{i}"):
                idx = events.index(e)
                del events[idx]
                world.data["events"] = events
                world.save_memory()
                st.warning("Evento eliminado.")
                st.experimental_rerun()

# -----------------------------------------------------------
# NARRATIVA DEL DÍA
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📖 Narrativa del Día")

today = datetime.now().strftime("%Y-%m-%d")

events_today = [e for e in events if e.get("date") == today]
emotion = stats.data.get("emotion", {})
boss = stats.data.get("bosses", {})
realms = stats.data.get("world", {}).get("realms", {})

narrative = f"### Capítulo del {today}\n\n"

# EMOCIONES
narrative += "#### 🧠 Estado interno:\n"
narrative += f"- Estrés: {emotion.get('stress', 0)}\n"
narrative += f"- Ansiedad: {emotion.get('anxiety', 0)}\n"
narrative += f"- Fatiga: {emotion.get('fatigue', 0)}\n\n"

# BOSS
if boss:
    narrative += f"#### 👹 Boss del Mes:\n- {boss.get('name')} — Fase {boss.get('phase')}\n\n"

# REINOS
narrative += "#### 🌍 Estado del Mundo:\n"
for realm, info in realms.items():
    narrative += f"- {realm.capitalize()}: progreso {info['progress']}%, reputación {info['reputation']}\n"

# EVENTOS DEL DÍA
narrative += "\n#### 📜 Eventos del día:\n"
if not events_today:
    narrative += "- No hubo eventos registrados hoy.\n"
else:
    for e in events_today:
        narrative += f"- ({e['type']}) {e.get('description', e.get('name',''))}\n"

st.write(narrative)

# -----------------------------------------------------------
# EXPORTAR NARRATIVA
# -----------------------------------------------------------
st.markdown("---")

if st.button("📘 Exportar capítulo del día"):
    chapter = memory.export_day_as_chapter(today)
    st.text_area("Capítulo generado:", chapter, height=400)

# -----------------------------------------------------------
# BACKUP DEL DÍA
# -----------------------------------------------------------
if st.button("📦 Guardar Backup"):
    r = memory.auto_backup()
    st.success(r)
