import streamlit as st
from modules.world import WorldManager
from modules.stats import StatsManager
from modules.memory import MemoryManager

st.set_page_config(
    page_title="Mundo — Aureon Nightweaver",
    layout="wide",
)

world = WorldManager()
stats = StatsManager()
memory = MemoryManager()

world.initialize_world()
realms = world.data["world"]["realms"]

# -----------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#A8C0FF;'>🌍 Mapa del Mundo</h1>
    <h3 style='color:#7F8CFF; margin-top:-10px;'>
        Reinos bajo la influencia de Aureon Nightweaver
    </h3>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------
# MOSTRAR REINOS
# -----------------------------------------------------------
st.markdown("## 🗺️ Reinos del Sistema Isekai")

cols = st.columns(3)
i = 0

for realm, data in realms.items():
    with cols[i % 3]:
        st.subheader(realm.capitalize())
        st.progress(data["progress"])
        st.write(f"Reputación: **{data['reputation']}**")
        st.write(f"Dificultad: {data['difficulty']} / 5")

        # Ajuste manual (si quieres actualizar por eventos)
        with st.expander("Ajustar valores"):
            new_progress = st.slider(
                f"{realm} — Progreso", 0, 100, data["progress"], key=f"prog_{realm}"
            )
            new_reputation = st.slider(
                f"{realm} — Reputación", 0, 100, data["reputation"], key=f"rep_{realm}"
            )
            new_difficulty = st.slider(
                f"{realm} — Dificultad", 1, 5, data["difficulty"], key=f"dif_{realm}"
            )

            if st.button(f"Guardar cambios en {realm}", key=f"save_{realm}"):
                realms[realm]["progress"] = new_progress
                realms[realm]["reputation"] = new_reputation
                realms[realm]["difficulty"] = new_difficulty
                world.save_memory()
                st.success("Valores actualizados para este reino.")
                st.experimental_rerun()

    i += 1

# -----------------------------------------------------------
# REGISTRAR EVENTO REAL
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🔥 Registrar Evento Real")

category = st.selectbox(
    "¿Qué categoría corresponde al evento?",
    ["work", "politics", "finance", "academia", "health", "family", "emotions"]
)

description = st.text_area("Describe lo que ocurrió:")

intensity = st.selectbox(
    "Intensidad del evento",
    [1, 2, 3],
    format_func=lambda x: {1:"Leve", 2:"Medio", 3:"Fuerte"}[x]
)

if st.button("Registrar Evento"):
    world.register_real_event(category, description, intensity)
    st.success("Evento registrado y aplicado al sistema.")
    st.experimental_rerun()

# -----------------------------------------------------------
# EVENTOS ALEATORIOS DEL MUNDO
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 💫 Generar Evento del Mundo (Aleatorio)")

if st.button("✨ Generar Evento Aleatorio"):
    event = world.generate_random_world_event()
    st.info(f"{event['name']}: {event['description']}")

# -----------------------------------------------------------
# NARRATIVA GLOBAL
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📜 Narrativa Global del Mundo")

# Construir narrativa según estados
text = "Los reinos reaccionan a las decisiones del Tejedor de Sombras.\n\n"

for realm, data in realms.items():
    if data["progress"] < 20:
        text += f"- **{realm.capitalize()}** está en estado frágil. El camino aún es incierto.\n"
    elif data["progress"] < 50:
        text += f"- **{realm.capitalize()}** comienza a estabilizarse. Se siente un leve avance.\n"
    elif data["progress"] < 80:
        text += f"- **{realm.capitalize()}** está fortaleciéndose. Los habitantes siguen tu influencia.\n"
    else:
        text += f"- **{realm.capitalize()}** prospera bajo tu liderazgo. La influencia de Aureon crece.\n"

st.write(text)

# -----------------------------------------------------------
# BACKUP
# -----------------------------------------------------------
st.markdown("---")
if st.button("📦 Guardar Backup del Mundo"):
    r = memory.auto_backup()
    st.success(r)
