import streamlit as st
from modules.stats import StatsManager
from modules.memory import MemoryManager
from datetime import datetime

st.set_page_config(page_title="Stats — Aureon Nightweaver", layout="wide")

# -----------------------------------------------------------
# LOAD STATS
# -----------------------------------------------------------
stats = StatsManager()
memory = MemoryManager()

base_stats = stats.base_stats()
final_stats = stats.final_stats()
emotion = stats.data.get("emotion", {})
effects = stats.active_effects()

# -----------------------------------------------------------
# TITLE
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#9BB0FF;'>
        📘 Estadísticas del Personaje — Aureon Nightweaver
    </h1>
    <h3 style='color:#7B88F7; margin-top:-10px;'>
        El Tejedor de Sombras y Estrategias
    </h3>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------
# STATS SECTION
# -----------------------------------------------------------
st.markdown("## 🧬 Stats Base vs Stats Finales")

cols = st.columns(3)

with cols[0]:
    st.subheader("Stats Base")
    st.json(base_stats)

with cols[1]:
    st.subheader("Stats Finales (con emoción y buffs)")
    st.json(final_stats)

with cols[2]:
    st.subheader("Diferencias")
    diffs = {k: final_stats[k] - base_stats.get(k,0) for k in base_stats}
    st.json(diffs)

# -----------------------------------------------------------
# EMOTIONAL STATE
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🧠 Estado Emocional")

emo_col1, emo_col2 = st.columns(2)

with emo_col1:
    st.write("### Valores actuales")
    st.json(emotion)

with emo_col2:
    st.write("### Ajustar emociones (por eventos reales)")
    new_emotion = {}
    for key, value in emotion.items():
        if key == "notes":
            continue
        new_emotion[key] = st.slider(
            key.capitalize(),
            0, 100, value
        )

    new_emotion["notes"] = st.text_area(
        "Notas del día", emotion.get("notes", "")
    )

    if st.button("Guardar estado emocional"):
        stats.data["emotion"] = new_emotion
        stats.save_memory()
        st.success("Estado emocional actualizado.")

# -----------------------------------------------------------
# BUFFS & DEBUFFS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ✨ Buffs y Debuffs Activos")

if effects:
    for e in effects:
        st.markdown(
            f"""
            <div style="background-color:#1f1f2e; padding:10px; border-radius:8px; margin-bottom:10px;">
                <b>{e['name']}</b><br>
                Desde: {e['start_date']}<br>
                Hasta: {e['end_date']}<br>
                Modificadores: {e['modifiers']}
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No hay buffs o debuffs activos.")

# -----------------------------------------------------------
# ADD MANUAL BUFF
# -----------------------------------------------------------
st.markdown("### ➕ Añadir Buff/Debuff Manual")

buff_name = st.text_input("Nombre del Buff/Debuff")
buff_days = st.number_input("Duración (días)", min_value=1, max_value=30, value=2)
buff_strength = st.number_input("Modificador a Fuerza", min_value=-5, max_value=5, value=0)
buff_int = st.number_input("Modificador a Inteligencia", min_value=-5, max_value=5, value=0)
buff_wis = st.number_input("Modificador a Sabiduría", min_value=-5, max_value=5, value=0)
buff_chr = st.number_input("Modificador a Carisma", min_value=-5, max_value=5, value=0)
buff_dex = st.number_input("Modificador a Destreza", min_value=-5, max_value=5, value=0)
buff_luck = st.number_input("Modificador a Suerte", min_value=-5, max_value=5, value=0)

if st.button("Aplicar Buff/Debuff"):
    mods = {
        "strength": buff_strength,
        "intelligence": buff_int,
        "wisdom": buff_wis,
        "charisma": buff_chr,
        "dexterity": buff_dex,
        "luck": buff_luck
    }
    stats.add_effect(buff_name, buff_days, mods)
    st.success("Buff/Debuff aplicado.")

# -----------------------------------------------------------
# ENERGY MANAGEMENT
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ⚡ Energía y Regeneración")

energy_change = st.number_input("Cambiar energía en:", -50, 50, 0)

if st.button("Aplicar cambio de energía"):
    stats.change_energy(energy_change)
    st.success("Energía actualizada.")

st.metric("Energía actual", stats.data["stats"]["energy"])

# -----------------------------------------------------------
# NARRATIVE SUMMARY
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📜 Resumen Narrativo del Estado Actual")

emo_text = """
Tu energía fluye de manera **{energy_state}**, tus emociones están en un estado **{mood}**,
y los hilos de tu poder actual se entrelazan con una influencia de **{buffs}** efectos activos.
"""
energy_state = "estable" if final_stats["energy"] > 50 else "frágil"
mood = emotion.get("mood", "neutral")
buffs_count = len(effects)

st.write(
    emo_text.format(
        energy_state=energy_state,
        mood=mood,
        buffs=buffs_count
    )
)

# -----------------------------------------------------------
# BACKUP
# -----------------------------------------------------------
st.markdown("---")
if st.button("📦 Crear Backup de Hoy"):
    result = memory.auto_backup()
    st.success(result)

