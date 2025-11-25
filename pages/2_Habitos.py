import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from modules.habits import HabitsManager

st.set_page_config(
    page_title="Hábitos — Sistema Isekai",
    layout="wide"
)

hm = HabitsManager()

# ============================================================
# CSS — estilo Solo Leveling / Notion híbrido
# ============================================================
st.markdown("""
<style>

body {
    background-color: #0D0F1A;
}

.habit-card {
    background: #13172A;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #1F2236;
    margin-bottom: 10px;
}

.habit-name {
    font-size: 18px;
    color: #B8C5FF;
    font-weight: 600;
}

.streak-badge {
    background: #1f1f32;
    padding: 6px 14px;
    border-radius: 8px;
    color: #9AA4FF;
    font-size: 14px;
    font-weight: bold;
    border: 1px solid #2A2E45;
}

.not-done {
    color: #FF6B6B;
    font-weight: 700;
}

.done {
    color: #7DFFAF;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================
st.markdown("""
<h1 style='color:#9BB0FF;'>📘 Tracker de Hábitos — Sistema Isekai</h1>
<h3 style='color:#7F88F7; margin-top:-10px;'>Progreso • Streaks • Bonificaciones • Evolución</h3>
""", unsafe_allow_html=True)

st.markdown("---")


# ============================================================
# FECHA HOY
# ============================================================
today = datetime.now().strftime("%Y-%m-%d")
weekday = datetime.now().strftime("%a")  # Mon, Tue...


# ============================================================
# LISTA DE HÁBITOS
# ============================================================
definitions = hm.get_definitions()
daily_log = hm.get_daily_log()
streaks = hm.get_streaks()

if today not in daily_log:
    daily_log[today] = {}

st.markdown("## 📅 Hábitos de Hoy")

for habit in definitions:

    # Mostrar solo los hábitos cuyo día coincide
    if weekday not in habit["days"]:
        continue

    habit_id = habit["id"]
    name = habit["name"]

    # Valor actual (True/False)
    current_value = daily_log[today].get(habit_id, False)

    col1, col2, col3 = st.columns([4,1,1])

    with col1:
        st.markdown(f"<div class='habit-name'>{name}</div>", unsafe_allow_html=True)

    with col2:
        if st.button("✔" if current_value else "✖", key=f"{habit_id}_{today}"):
            hm.toggle_habit(habit_id, today)
            st.experimental_rerun()

    with col3:
        streak_value = streaks.get(habit_id, 0)
        st.markdown(
            f"<span class='streak-badge'>🔥 {streak_value} días</span>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)


st.markdown("---")


# ============================================================
# GRÁFICO SEMANAL
# ============================================================
st.markdown("## 📊 Resumen Semanal (Últimos 7 días)")

week_start = datetime.now() - timedelta(days=6)
summary = hm.get_week_summary(week_start)

df = pd.DataFrame({
    "Día": [(week_start + timedelta(days=i)).strftime("%a") for i in range(7)],
    "Completados": summary
})

fig, ax = plt.subplots(figsize=(8,3))
ax.bar(df["Día"], df["Completados"])
ax.set_title("Hábitos Completados por Día (Semana Actual)")
ax.set_ylabel("Cantidad")
ax.set_ylim(0, max(summary) + 1)

st.pyplot(fig)


# ============================================================
# RESUMEN ESTADÍSTICO
# ============================================================
st.markdown("---")
st.markdown("## 📈 Estadísticas de la Semana")

total_completed = sum(summary)
best_day = df.loc[df["Completados"].idxmax(), "Día"]

colA, colB, colC = st.columns(3)
colA.metric("Total completados", total_completed)
colB.metric("Mejor día", best_day)
colC.metric("Hábito más fuerte", max(streaks, key=streaks.get) if streaks else "N/A")


# ============================================================
# OPCIÓN: AGREGAR NUEVOS HÁBITOS (Manual)
# ============================================================
with st.expander("➕ Agregar un hábito nuevo"):
    st.info("Puedes agregar hábitos adicionales sin afectar los ya existentes.")

    new_name = st.text_input("Nombre del hábito")
    new_id = st.text_input("ID único del hábito (sin espacios)")
    new_days = st.multiselect(
        "Días:",
        ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    )

    st.markdown("### Efectos del hábito")
    eff_energy = st.number_input("Energy", value=0)
    eff_mot = st.number_input("Motivation", value=0)
    eff_int = st.number_input("Intelligence", value=0)
    eff_cha = st.number_input("Charisma", value=0)
    eff_wis = st.number_input("Wisdom", value=0)
    eff_cla = st.number_input("Clarity", value=0)

    if st.button("Crear hábito"):
        new_habit = {
            "id": new_id,
            "name": new_name,
            "days": new_days,
            "effects": {
                "energy": eff_energy,
                "motivation": eff_mot,
                "intelligence": eff_int,
                "charisma": eff_cha,
                "wisdom": eff_wis,
                "clarity": eff_cla
            }
        }

        hm.habits["definitions"].append(new_habit)
        hm.save_json(hm.habits_path, hm.habits)
        st.success("Hábito agregado con éxito. Recarga la página.")
        st.experimental_rerun()
