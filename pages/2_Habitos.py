import streamlit as st
import pandas as pd
from datetime import datetime, date
from modules.memory import MemoryManager
from modules.stats import StatsManager
from modules.domains import DomainManager

st.set_page_config(page_title="Hábitos — Sistema Isekai", layout="wide")

mem = MemoryManager()
stats = StatsManager()
domains = DomainManager()
data = mem.data

# -----------------------------------------------------------
# CSS SOLO LEVELING / NOTION STYLE
# -----------------------------------------------------------
st.markdown("""
<style>

    .habit-card {
        background: #151827;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2A2F45;
        margin-bottom: 15px;
        box-shadow: 0px 0px 15px rgba(80,100,255,0.07);
    }

    .habit-title {
        font-size: 20px;
        color: #A9B9FF;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .habit-group-title {
        font-size: 26px;
        color: #90A2FF;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .metric-box {
        background: #10121F;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #23273A;
        color: #A9B9FF;
        font-size: 17px;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# HOY
# -----------------------------------------------------------
today = date.today().strftime("%Y-%m-%d")

if "habits" not in data:
    st.error("No existe la sección 'habits' en tu JSON.")
    st.stop()

definitions = data["habits"]["definitions"]
daily_log = data["habits"].get("daily_log", {})

if today not in daily_log:
    daily_log[today] = {}

# Diccionario para clasificar hábitos
habit_groups = {
    "Rutina": [],
    "Mente": [],
    "Academia": [],
    "Salud": [],
    "Personal": []
}

# Clasificación automática por nombre (puedes editar esto luego)
for h in definitions:
    name = h["name"].lower()
    if "5am" in name or "día" in name:
        habit_groups["Rutina"].append(h)
    elif "inglés" in name or "leer" in name:
        habit_groups["Academia"].append(h)
    elif "dormir" in name:
        habit_groups["Rutina"].append(h)
    elif "agua" in name or "ducha" in name or "ejercicio" in name:
        habit_groups["Salud"].append(h)
    else:
        habit_groups["Personal"].append(h)


# -----------------------------------------------------------
# APLICAR EFECTOS
# -----------------------------------------------------------
def apply_habit_effects(habit):
    effects = habit.get("effects", {})

    # emoción
    emo = data["emotion"]
    for e in ["motivation", "clarity", "energy", "fatigue", "stress", "anxiety"]:
        if e in effects:
            emo[e] = max(0, min(100, emo[e] + effects[e]))

    # stats
    s = data["stats"]
    for stt in ["strength", "intelligence", "wisdom", "charisma", "dexterity", "luck"]:
        if stt in effects:
            s[stt] = max(0, s[stt] + effects[stt])

    # domains
    if "domains" in effects:
        for d, val in effects["domains"].items():
            domains.add_exp(d, val)

    mem.save_memory()


# -----------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------
st.markdown("""
<h1 style='color:#AFC2FF;'>📘 Sistema de Hábitos — Aureon Nightweaver</h1>
<h3 style='color:#7D8FFF;'>Disciplina · Crecimiento · Leveling</h3>
<hr>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# DASHBOARD SUPERIOR (Estilo Notion)
# -----------------------------------------------------------

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("<div class='metric-box'>📅 Día: <b>" + today + "</b></div>", unsafe_allow_html=True)

with colB:
    completion_today = sum(daily_log[today].values()) if daily_log[today] else 0
    total_today = len(definitions)
    percent = int((completion_today / total_today) * 100) if total_today > 0 else 0
    st.markdown(f"<div class='metric-box'>🔥 Progreso de Hoy: <b>{percent}%</b></div>", unsafe_allow_html=True)

with colC:
    streak = data["habits"].get("streak", 0)
    st.markdown(f"<div class='metric-box'>🎖️ Streak: <b>{streak} días</b></div>", unsafe_allow_html=True)


# -----------------------------------------------------------
# HABITOS DEL DÍA (Vista Notion)
# -----------------------------------------------------------
st.markdown("## 🧩 Hábitos del Día\n")

weekday = datetime.today().strftime("%a")  # "Mon", "Tue", etc.

for group, habits in habit_groups.items():
    if len(habits) == 0:
        continue

    st.markdown(f"<div class='habit-group-title'>{group}</div>", unsafe_allow_html=True)

    for h in habits:

        # si el hábito NO aplica para hoy, se salta
        if weekday not in h["days"]:
            continue

        hid = h["id"]
        completed = daily_log[today].get(hid, False)

        with st.container():
            st.markdown("<div class='habit-card'>", unsafe_allow_html=True)

            col1, col2 = st.columns([4,1])

            with col1:
                st.markdown(f"<div class='habit-title'>{h['name']}</div>", unsafe_allow_html=True)

            with col2:
                checked = st.checkbox("", value=completed, key=f"{today}_{hid}")

                if checked != completed:
                    daily_log[today][hid] = checked

                    # aplicar efectos si se acaba de completar
                    if checked:
                        apply_habit_effects(h)

                    mem.save_memory()

            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------
# CÁLCULO DE STREAK
# -----------------------------------------------------------
def calculate_streak():
    streak = 0
    days = sorted(list(daily_log.keys()))

    for d in reversed(days):
        done = all(daily_log[d].values()) if d in daily_log and len(daily_log[d]) > 0 else False
        if done:
            streak += 1
        else:
            break

    return streak


data["habits"]["streak"] = calculate_streak()
mem.save_memory()


# -----------------------------------------------------------
# GRÁFICOS DE TENDENCIA (Estilo Notion)
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📊 Gráficos de Progreso (Notion Style)")

# convertir a DataFrame
records = []
for d, logs in daily_log.items():
    if len(logs) == 0:
        continue
    pct = int((sum(logs.values()) / len(definitions)) * 100)
    records.append({"day": d, "completion": pct})

if len(records) > 0:
    df = pd.DataFrame(records)

    st.line_chart(df.set_index("day"))

else:
    st.info("Aún no hay datos suficientes para gráficos.")


# -----------------------------------------------------------
# HISTORIAL DE HÁBITOS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📜 Historial de Hábitos")

for d, logs in sorted(daily_log.items())[::-1]:
    pct = int((sum(logs.values()) / len(definitions)) * 100)
    st.write(f"**{d}** — {pct}% completado")


st.success("Sistema de hábitos cargado correctamente.")
