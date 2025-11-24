import streamlit as st
from modules.bosses import BossManager
from modules.stats import StatsManager
from modules.missions import MissionManager
from modules.memory import MemoryManager
from datetime import datetime

st.set_page_config(page_title="Boss del Mes — Aureon Nightweaver", layout="wide")

boss = BossManager()
stats = StatsManager()
missions = MissionManager()
memory = MemoryManager()

boss_data = boss.get_current_boss()

# -----------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#A8B0FF;'>👹 Boss del Mes</h1>
    <h3 style='color:#7C82FF; margin-top:-10px;'>
        Campo de Batalla de Aureon Nightweaver
    </h3>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------
# SI NO HAY BOSS ACTIVO
# -----------------------------------------------------------
if not boss_data:
    st.warning("No hay un Boss activo este mes.")

    bosses_available = list(boss.define_bosses().keys())
    selected = st.selectbox("Selecciona un Boss para iniciar la batalla:", bosses_available)

    if st.button("Iniciar Boss del Mes"):
        boss.start_boss_battle(selected)
        st.success(f"Boss `{selected}` invocado.")
        st.experimental_rerun()

    st.stop()

# -----------------------------------------------------------
# SI HAY BOSS ACTIVO
# -----------------------------------------------------------

st.markdown(f"## 👑 Boss Actual: **{boss_data['name']}**")

phases = boss.define_bosses()[boss_data["name"]]["phases"]
current_phase = phases[boss_data["phase"] - 1]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Estado General")
    st.write(f"**Nombre:** {boss_data['name']}")
    st.write(f"**Fase actual:** {boss_data['phase']} / {boss_data['total_phases']}")
    st.write(f"**Ataque actual:** {current_phase['attack_description']}")
    st.write(f"**Debuff de fase:** {current_phase['debuff']}")
    st.write(f"**Misión de contraataque:** {current_phase['mission_objective']}")

with col2:
    st.subheader("HP del Boss")
    hp = boss_data["current_hp"]
    st.progress(int((hp / 100) * 100))
    st.write(f"HP restante: **{hp}**")

# -----------------------------------------------------------
# HACER DAÑO AL BOSS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ⚔️ Atacar al Boss")

damage = st.slider("Daño a infligir", 1, 50, 10)

if st.button("⚡ Atacar / Reducir HP"):
    updated = boss.damage_boss(damage)

    if updated.get("defeated"):
        st.success("🎉 ¡Has derrotado al Boss del Mes!")
    else:
        st.success(f"Daño infligido. HP actual: {updated['current_hp']}")

    st.experimental_rerun()

# -----------------------------------------------------------
# ATAQUE DEL BOSS BASADO EN EMOCIÓN
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 💢 Ataque del Boss (dependiendo de tu estado emocional)")

if st.button("🔮 Forzar ataque del Boss"):
    result = boss.boss_attack()
    st.warning(result)
    st.experimental_rerun()

# -----------------------------------------------------------
# MISIONES DE RAID
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🛡️ Misiones de Raid contra el Boss")

raid_mission = {
    "title": f"Contraataque a {boss_data['name']} (Fase {boss_data['phase']})",
    "description": current_phase["mission_objective"],
    "difficulty": boss_data['phase'] + 1,
    "reward_exp": 40 + (boss_data['phase'] * 20),
}

with st.expander("Ver Misión de Raid Actual"):
    st.write(f"**Título:** {raid_mission['title']}")
    st.write(f"**Descripción:** {raid_mission['description']}")
    st.write(f"**Recompensa:** {raid_mission['reward_exp']} EXP")

    if st.button("Añadir como Side Quest"):
        missions.create_mission(
            raid_mission["title"],
            raid_mission["description"],
            "side_quests",
            raid_mission["difficulty"],
            raid_mission["reward_exp"],
            3
        )
        st.success("Misión de raid añadida a Side Quests.")

# -----------------------------------------------------------
# NARRATIVA DINÁMICA
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📜 Narrativa")

phase_name = current_phase["name"]
emotion = stats.data["emotion"]

mood = emotion.get("mood", "neutral")
stress = emotion.get("stress", 0)
fatigue = emotion.get("fatigue", 0)
anxiety = emotion.get("anxiety", 0)

narrative = f"""
En esta fase, **{boss_data['name']}** despliega su poder:
**{phase_name}**, un estado donde su alma influye directamente en tus emociones.

Tu estrés actual es **{stress}**, tu fatiga es **{fatigue}**, y tu ansiedad es **{anxiety}**.

El Boss observa tu estado y sus sombras reaccionan al más mínimo temblor interior.
"""

if stress > 70 or fatigue > 70:
    narrative += "\n\n⚠️ **El Boss huele tu fragilidad. Su poder aumenta.**"
elif stress < 30 and anxiety < 30:
    narrative += "\n\n✨ **Tu mente está firme. Las sombras del Boss flaquean.**"

st.write(narrative)

# -----------------------------------------------------------
# CONTROLES AVANZADOS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ⚙️ Controles Avanzados del Boss")

colA, colB = st.columns(2)

with colA:
    if st.button("🧹 Reiniciar Boss del Mes"):
        boss.data["bosses"] = {}
        boss.save_memory()
        st.success("Boss reiniciado.")
        st.experimental_rerun()

with colB:
    bosses_available = list(boss.define_bosses().keys())
    new_boss = st.selectbox("Iniciar nuevo Boss:", bosses_available)

    if st.button("⚔️ Invocar nuevo Boss"):
        boss.start_boss_battle(new_boss)
        st.success(f"Nuevo Boss invocado: {new_boss}")
        st.experimental_rerun()

# -----------------------------------------------------------
# BACKUP
# -----------------------------------------------------------
st.markdown("---")
if st.button("📦 Guardar Backup del Sistema"):
    r = memory.auto_backup()
    st.success(r)
