import streamlit as st
from datetime import datetime
from modules.stats import StatsManager   # ESTE es el que sí tiene "data"

st.set_page_config(page_title="Hábitos — Sistema Isekai", layout="wide")

# -----------------------------------------------
# Cargar JSON completo
# -----------------------------------------------
sm = StatsManager()
data = sm.data

if "habits" not in data:
    st.error("Falta el campo 'habits' en system_memory.json")
    st.stop()

habits = data["habits"]["definitions"]
daily_log = data["habits"].get("daily_log", {})

today = datetime.now().strftime("%Y-%m-%d")

if today not in daily_log:
    daily_log[today] = {}

# -----------------------------------------------
# CSS estilo Solo Leveling
# -----------------------------------------------
st.markdown("""
<style>
    .habit-card {
        background: #141624;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #1F2236;
        margin-bottom: 12px;
        box-shadow: 0px 0px 15px rgba(80,100,255,0.07);
    }
    .habit-title {
        font-size: 18px;
        color: #A9B9FF;
        font-weight: 600;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Título
# -----------------------------------------------
st.markdown("""
<h1 style='color:#9BB0FF;'>📘 Sistema de Hábitos</h1>
<h3 style='color:#7F8AFF; margin-top:-10px;'>Progresión diaria • Influencia en Stats • Crecimiento a largo plazo</h3>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------
# LISTA DE HÁBITOS
# -----------------------------------------------
st.subheader(f"Hábitos de hoy — {today}")

for habit in habits:

    h_id = habit["id"]
    h_name = habit["name"]

    if h_id not in daily_log[today]:
        daily_log[today][h_id] = False

    checked = st.checkbox(
        label=h_name,
        value=daily_log[today][h_id],
        key=f"chk_{h_id}"
    )

    daily_log[today][h_id] = checked

# Guardar progreso diario
data["habits"]["daily_log"] = daily_log
sm.save_memory()

st.success("Progreso diario guardado.")

# -----------------------------------------------
# ESTADÍSTICAS SEMANALES
# -----------------------------------------------
st.markdown("---")
st.subheader("📊 Estadísticas Semanales")

week_counts = {habit["id"]: 0 for habit in habits}

for day, records in daily_log.items():
    for h_id, done in records.items():
        if done:
            week_counts[h_id] += 1

for habit in habits:
    h_id = habit["id"]
    h_name = habit["name"]
    count = week_counts[h_id]

    st.markdown(f"**{h_name}:** {count} / 7 días")

# -----------------------------------------------
# APLICAR BONIFICACIONES A STATS (SEMANAL)
# -----------------------------------------------
st.markdown("---")
st.subheader("⚡ Bonificaciones Semanales por Consistencia")

if st.button("Aplicar bonificaciones de esta semana"):

    for habit in habits:
        h_id = habit["id"]
        done_days = week_counts[h_id]

        # necesita mínimo 4 días para bonificación
        if done_days >= 4:
            effects = habit["effects"]

            # aplicar efectos emocionales / stats
            for stat, val in effects.items():
                if stat == "domains":
                    for dom_key, exp_gain in val.items():
                        data["domains"][dom_key]["exp"] += exp_gain
                else:
                    if stat in data["emotion"]:
                        data["emotion"][stat] += val
                    elif stat in data["stats"]:
                        data["stats"][stat] += val

    sm.save_memory()
    st.success("Bonificaciones aplicadas correctamente.")

