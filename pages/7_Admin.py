import streamlit as st
from modules.stats import StatsManager
from modules.bosses import BossManager
from modules.world import WorldManager
from modules.memory import MemoryManager
import json

st.set_page_config(
    page_title="Admin — Aureon Nightweaver",
    layout="wide"
)

stats = StatsManager()
boss = BossManager()
world = WorldManager()
memory = MemoryManager()

# -----------------------------------------------------------
# TITULO
# -----------------------------------------------------------
st.markdown(
    """
    <h1 style='color:#FF9999;'>⚙️ Panel Administrativo</h1>
    <h3 style='color:#FFCCCC; margin-top:-10px;'>
        Control total del Sistema — SOLO PARA AUREON NIGHTWEAVER
    </h3>
    """,
    unsafe_allow_html=True
)

st.warning("⚠ Esta sección permite modificar directamente variables del sistema. Úsala con sabiduría.")

# -----------------------------------------------------------
# EDITAR STATS
# -----------------------------------------------------------
st.markdown("## 🧬 Editar Stats del Personaje")

col1, col2, col3 = st.columns(3)

with col1:
    for stat in ["strength", "intelligence", "wisdom"]:
        new_val = st.number_input(f"{stat.capitalize()}", 0, 99, stats.data["stats"].get(stat, 10))
        if st.button(f"Guardar {stat}"):
            stats.data["stats"][stat] = new_val
            stats.save_memory()
            st.success(f"{stat} actualizado.")

with col2:
    for stat in ["charisma", "dexterity", "luck"]:
        new_val = st.number_input(f"{stat.capitalize()}", 0, 99, stats.data["stats"].get(stat, 10), key=f"stat_{stat}")
        if st.button(f"Guardar {stat}", key=f"save_{stat}"):
            stats.data["stats"][stat] = new_val
            stats.save_memory()
            st.success(f"{stat} actualizado.")

with col3:
    energy = st.number_input("Energía", 0, 200, stats.data["stats"]["energy"])
    max_energy = st.number_input("Máx Energía", 10, 200, stats.data["stats"]["max_energy"])

    if st.button("Guardar Energía"):
        stats.data["stats"]["energy"] = energy
        stats.data["stats"]["max_energy"] = max_energy
        stats.save_memory()
        st.success("Energía actualizada.")

# -----------------------------------------------------------
# EDITAR EMOCIONES
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🧠 Editar Estado Emocional")

emotion = stats.data.get("emotion", {})

for key, value in emotion.items():
    if key != "notes":
        new_value = st.slider(key, 0, 100, value)
        emotion[key] = new_value

emotion["notes"] = st.text_area("Notas del estado emocional", emotion.get("notes", ""))

if st.button("Guardar Emociones"):
    stats.data["emotion"] = emotion
    stats.save_memory()
    st.success("Estado emocional actualizado.")

# -----------------------------------------------------------
# CONTROL DEL BOSS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 👹 Control del Boss")

boss_data = boss.get_current_boss()

if boss_data:
    st.write(f"Boss actual: **{boss_data['name']}** — Fase {boss_data['phase']}")
    new_hp = st.number_input("HP del Boss", 0, 200, boss_data["current_hp"])

    if st.button("Guardar HP"):
        boss_data["current_hp"] = new_hp
        boss.save_memory()
        st.success("HP actualizado.")

    if st.button("Eliminar Boss Actual"):
        boss.data["bosses"] = {}
        boss.save_memory()
        st.warning("Boss eliminado.")
        st.experimental_rerun()

else:
    st.info("No hay boss activo.")

# -----------------------------------------------------------
# CONTROL DEL MUNDO
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🌍 Control del Mundo")

realms = world.data.get("world", {}).get("realms", {})

for realm, info in realms.items():
    st.subheader(realm.capitalize())
    colA, colB, colC = st.columns(3)

    with colA:
        progress = st.number_input(
            f"Progreso ({realm})", 0, 100, info["progress"],
            key=f"progress_{realm}"
        )
    with colB:
        rep = st.number_input(
            f"Reputación ({realm})", 0, 100, info["reputation"],
            key=f"rep_{realm}"
        )
    with colC:
        difficulty = st.number_input(
            f"Dificultad ({realm})", 1, 5, info["difficulty"],
            key=f"diff_{realm}"
        )

    if st.button(f"Guardar cambios en {realm}", key=f"save_{realm}"):
        realms[realm]["progress"] = progress
        realms[realm]["reputation"] = rep
        realms[realm]["difficulty"] = difficulty
        world.save_memory()
        st.success(f"Reino {realm} actualizado.")

# -----------------------------------------------------------
# BOTONES AVANZADOS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🔥 Acciones Avanzadas")

colX, colY = st.columns(2)

with colX:
    if st.button("🧹 Limpiar TODOS los eventos"):
        world.data["events"] = []
        world.save_memory()
        st.warning("Todos los eventos eliminados.")

    if st.button("🧨 Reset Total del Mundo"):
        world.data["world"]["realms"] = world.define_world()
        world.save_memory()
        st.error("Mundo reiniciado a estado base.")

with colY:
    if st.button("🗑 Eliminar TODOS los buffs y debuffs"):
        stats.data["effects"] = []
        stats.save_memory()
        st.success("Todos los efectos eliminados.")

    if st.button("🔄 Restauración limpia del sistema"):
        stats.data["effects"] = []
        stats.data["emotion"] = {k: 50 for k in stats.data["emotion"].keys()}
        world.data["events"] = []
        boss.data["bosses"] = {}
        stats.save_memory()
        world.save_memory()
        boss.save_memory()
        memory.auto_backup()
        st.error("Sistema reseteado a estado neutral.")

# -----------------------------------------------------------
# VER JSON CRUDO
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🧾 Ver Memoria Cruda (JSON)")

with st.expander("Mostrar JSON Completo"):
    st.json(memory.load_memory())
