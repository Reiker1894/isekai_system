import streamlit as st
from modules.missions import MissionManager
from modules.stats import StatsManager
from modules.memory import MemoryManager
from datetime import datetime

st.set_page_config(page_title="Misiones — Aureon Nightweaver", layout="wide")

missions = MissionManager()
stats = StatsManager()
memory = MemoryManager()

# -----------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#9BB0FF;'>
        📅 Misiones del Sistema — Aureon Nightweaver
    </h1>
    <h3 style='color:#7B88F7; margin-top:-10px;'>
        Camino del Estratega • Progresión Diaria y Semanal
    </h3>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------------------------------------
# GENERAR MISIONES
# -----------------------------------------------------------
st.markdown("## ⚡ Generar Misiones")

col_gen1, col_gen2 = st.columns(2)

with col_gen1:
    if st.button("🎯 Generar Misiones Diarias"):
        missions.generate_daily_missions()
        st.success("Misiones diarias generadas.")

with col_gen2:
    if st.button("📆 Generar Misiones Semanales"):
        missions.generate_weekly_missions()
        st.success("Misiones semanales generadas.")

# -----------------------------------------------------------
# MOSTRAR MISIONES POR CATEGORÍA
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📘 Misiones Activas")

mission_types = {
    "daily": "🟦 Diarias",
    "weekly": "🟨 Semanales",
    "side_quests": "🟪 Secundarias",
    "main_quest": "🟥 Misión Principal"
}

data = stats.data["missions"]

# DAILY & WEEKLY
for mtype, title in mission_types.items():
    st.markdown(f"### {title}")

    if mtype in ["daily", "weekly", "side_quests"]:
        if len(data[mtype]) == 0:
            st.info("No hay misiones en esta categoría.")
        else:
            for i, m in enumerate(data[mtype]):
                box_color = "#1b1b2e" if m["status"] == "pending" else "#233"
                with st.expander(f"{m['title']}"):
                    st.markdown(
                        f"""
                        <div style="background-color:{box_color}; padding:12px; border-radius:8px;">
                            <b>Descripción:</b> {m['description']}<br>
                            <b>Dificultad:</b> {m['difficulty']}<br>
                            <b>Recompensa:</b> {m['reward_exp']} XP<br>
                            <b>Estado:</b> {m['status']}<br>
                            <b>Deadline:</b> {m['deadline']}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if m["status"] == "pending":
                        if st.button(f"✔ Completar Misión {i} ({mtype})"):
                            missions.complete_mission(mtype, i)
                            st.success("¡Misión completada!")
                            st.experimental_rerun()

    # MAIN QUEST
    if mtype == "main_quest":
        if data["main_quest"] == {}:
            st.info("No hay misión principal activa.")
        else:
            m = data["main_quest"]
            with st.expander(f"🟥 {m['title']}"):
                st.write(m)
                if m["status"] == "pending":
                    if st.button("🔥 Completar Misión Principal"):
                        m["status"] = "completed"
                        stats.save_memory()
                        st.success("¡Misión principal completada!")

# -----------------------------------------------------------
# MISIONES FALLIDAS AUTOMÁTICAMENTE
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ❌ Misiones Fallidas por Deadline")

failed = missions.fail_expired_missions()

if failed:
    for m in failed:
        st.error(f"Misión fallida: {m['title']} — {m['deadline']}")
else:
    st.info("No hay misiones vencidas por ahora.")

# -----------------------------------------------------------
# CREAR MISIÓN MANUAL
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ➕ Crear Nueva Misión Manual")

title = st.text_input("Título de la misión")
desc = st.text_area("Descripción")
difficulty = st.slider("Dificultad", 1, 4, 2)
reward = st.number_input("Recompensa (XP)", 10, 500, 50)
mtype = st.selectbox("Tipo", ["daily", "weekly", "side_quests"])
deadline_days = st.number_input("Días para el deadline", 1, 30, 1)

if st.button("Crear Misión"):
    missions.create_mission(title, desc, mtype, difficulty, reward, deadline_days)
    st.success("Misión creada exitosamente.")

# -----------------------------------------------------------
# RESUMEN NARRATIVO
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📜 Narrativa del Sistema")

daily_count = len(data["daily"])
weekly_count = len(data["weekly"])
side_count = len(data["side_quests"])

story = f"""
Hoy, Aureon Nightweaver enfrenta **{daily_count} misiones diarias**, 
**{weekly_count} semanales** y **{side_count} secundarias**.

El flujo del destino se entrelaza con los plazos marcados por el Sistema.
"""

st.info(story)

# -----------------------------------------------------------
# BACKUP
# -----------------------------------------------------------
if st.button("📦 Crear Backup del Día"):
    msg = memory.auto_backup()
    st.success(msg)
