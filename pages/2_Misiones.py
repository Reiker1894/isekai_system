import streamlit as st
from modules.missions import MissionManager
from modules.stats import StatsManager
from modules.memory import MemoryManager
from datetime import datetime

st.set_page_config(page_title="Misiones — Aureon Nightweaver", layout="wide")

missions = MissionManager()
stats = StatsManager()
memory = MemoryManager()

data = missions.data

# -----------------------------------------------------------
# SOLO LEVELING CSS
# -----------------------------------------------------------
st.markdown("""
<style>

    .mission-card {
        background: #141624;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #1F2236;
        margin-bottom: 12px;
        box-shadow: 0px 0px 15px rgba(80,100,255,0.07);
    }

    .mission-title {
        font-size: 21px;
        color: #A9B9FF;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .mission-info {
        color: #DADFFF; 
        font-size: 15px;
        margin-bottom: 4px;
    }

    .difficulty-badge {
        background: #1f1f32;
        padding: 4px 10px;
        border-radius: 8px;
        color: #9AA4FF;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #2A2E45;
        margin-right: 8px;
    }

    .reward-box {
        background: #10121f;
        border: 1px solid #22263A;
        padding: 8px;
        border-radius: 8px;
        margin-top: 4px;
        color: #A7B3FF;
    }

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown("""
<h1 style='color:#9BB0FF;'>
    📅 Misiones — Sistema Isekai de Aureon Nightweaver
</h1>
<h3 style='color:#7F88F7; margin-top:-10px;'>
    Camino del Estratega • Progresión Diaria y Semanal
</h3>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------
# GENERAR MISIONES
# -----------------------------------------------------------
st.subheader("⚡ Generar Misiones Automáticas")

c1, c2 = st.columns(2)

with c1:
    if st.button("🎯 Generar Misiones Diarias"):
        missions.generate_daily_missions()
        st.success("Misiones diarias generadas correctamente.")

with c2:
    if st.button("📆 Generar Misiones Semanales"):
        missions.generate_weekly_missions()
        st.success("Misiones semanales generadas correctamente.")

st.markdown("---")

# -----------------------------------------------------------
# VISUALIZACIÓN DE MISIONES
# -----------------------------------------------------------
st.subheader("📘 Misiones Activas")

mission_types = {
    "daily": "🟦 Diarias",
    "weekly": "🟨 Semanales",
    "side_quests": "🟪 Secundarias"
}

for mtype, title in mission_types.items():

    st.markdown(f"## {title}")

    if len(data["missions"][mtype]) == 0:
        st.info("No hay misiones en esta categoría.")
        continue

    for i, m in enumerate(data["missions"][mtype]):

        # --------------------------------------------------------
        # 🔧 Parche automático para misiones antiguas
        # --------------------------------------------------------
        if "reward_dark" not in m:
            m["reward_dark"] = 0
            missions.save_memory()

        color = (
            "#141624" if m["status"] == "pending"
            else "#132018" if m["status"] == "completed"
            else "#2B1A1A"
        )

        with st.container():
            st.markdown(f"<div class='mission-card' style='background:{color};'>", unsafe_allow_html=True)

            # ------------------------------------------------------
            # HEADER
            # ------------------------------------------------------
            st.markdown(
                f"<div class='mission-title'>{m['title']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='mission-info'><b>Descripción:</b> {m['description']}</div>",
                unsafe_allow_html=True
            )

            # ------------------------------------------------------
            # BADGES (XP, DARK POINTS)
            # ------------------------------------------------------
            badge = f"""
            <span class='difficulty-badge'>
                🗡️ Dificultad: {m['difficulty']}
            </span>
            <span class='difficulty-badge'>
                🎁 EXP: {m['reward_exp']}
            </span>
            <span class='difficulty-badge'>
                🌑 Dark Points: +{m.get('reward_dark', 0)}
            </span>
            """

            st.markdown(badge, unsafe_allow_html=True)

            # ------------------------------------------------------
            # DEADLINE + STATUS
            # ------------------------------------------------------
            st.markdown(
                f"<div class='reward-box'><b>⏳ Deadline:</b> {m['deadline']}<br>"
                f"<b>📌 Estado:</b> {m['status']}</div>",
                unsafe_allow_html=True
            )

            # ------------------------------------------------------
            # BOTÓN COMPLETAR
            # ------------------------------------------------------
            if m["status"] == "pending":
                if st.button(f"✔ Completar «{m['title']}»", key=f"{mtype}_{i}"):
                    missions.complete_mission(mtype, i)
                    st.success("¡Misión completada! Recompensas aplicadas.")
                    st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
# FALLOS AUTOMÁTICOS
# -----------------------------------------------------------
st.markdown("---")
st.subheader("❌ Misiones Fallidas Automáticamente")

failed = missions.fail_expired_missions()

if failed:
    for m in failed:
        st.error(f"⚠ {m['title']} — Deadline: {m['deadline']}")
else:
    st.info("No hay misiones vencidas.")

# -----------------------------------------------------------
# CREAR MISIÓN MANUAL
# -----------------------------------------------------------
st.markdown("---")
st.subheader("➕ Crear Misión Manual")

title = st.text_input("Título")
desc = st.text_area("Descripción")
base_diff = st.slider("Dificultad Base (antes de ajustes del sistema)", 1, 4, 2)
mtype = st.selectbox("Tipo", ["daily", "weekly", "side_quests"])
deadline_days = st.number_input("Días para deadline", 1, 30, 1)

if st.button("Crear"):
    missions.create_mission(title, desc, mtype, base_diff, deadline_days)
    st.success("Misión creada correctamente.")

# -----------------------------------------------------------
# DARK POINTS + RESUMEN
# -----------------------------------------------------------
st.markdown("---")
st.subheader("🌑 Resumen del Sistema")

dp = data.get("dark_points", 0)

st.markdown(f"""
### 🌑 Dark Points Acumulados: **{dp}**

Cada misión completada alimenta tu crecimiento interior  
y desbloquea recompensas que puedes adquirir en la sección **Admin**.
""")

# -----------------------------------------------------------
# BACKUP
# -----------------------------------------------------------
if st.button("📦 Backup"):
    msg = memory.auto_backup()
    st.success(msg)
