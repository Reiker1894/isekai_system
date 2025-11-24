import streamlit as st
from PIL import Image
import os
from modules.stats import StatsManager
from modules.missions import MissionManager
from modules.bosses import BossManager
from modules.world import WorldManager
from modules.memory import MemoryManager

# -----------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA (TEMA OSCURO RPG)
# -----------------------------------------------------------
st.set_page_config(
    page_title="Aureon Nightweaver — Strategic Worldbuilder",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------
# PLACEHOLDER DEL AVATAR
# -----------------------------------------------------------
AVATAR_PATH = "data/avatar_placeholder.png"

# Si el avatar no existe, crea un cuadrado temporal
if not os.path.exists(AVATAR_PATH):
    from PIL import ImageDraw
    img = Image.new("RGB", (300, 300), color=(20, 20, 40))
    d = ImageDraw.Draw(img)
    d.text((40, 140), "AVATAR", fill=(150, 150, 255))
    img.save(AVATAR_PATH)

# -----------------------------------------------------------
# INICIALIZACIÓN DE MANAGERS
# -----------------------------------------------------------
stats = StatsManager()
missions = MissionManager()
bosses = BossManager()
world = WorldManager()
memory = MemoryManager()

# -----------------------------------------------------------
# CABECERA RPG DEL HUD
# -----------------------------------------------------------
with st.container():
    col_avatar, col_info = st.columns([1, 3])

    with col_avatar:
        st.image(AVATAR_PATH, width=200)

    with col_info:
        st.markdown(
            """
            <h1 style='color:#A8C0FF; font-size: 48px;'>
                Aureon Nightweaver
            </h1>
            <h3 style='color:#7F8CFF; margin-top:-15px;'>
                Strategic Worldbuilder • Renacido del Fénix
            </h3>
            """,
            unsafe_allow_html=True
        )

        # Botón especial del sistema diario
        if st.button("⚡ ACTIVAR SISTEMA DEL DÍA"):
            # generar misiones diarias
            missions.generate_daily_missions()
            # evento aleatorio
            world.generate_random_world_event()
            # backup
            memory.auto_backup()
            st.success("Sistema del Día Activado. Nuevas misiones y eventos generados.")

# -----------------------------------------------------------
# HEADER DE STATS + BOSS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📊 Estado del Personaje")

final_stats = stats.final_stats()
base_stats = stats.base_stats()

col1, col2, col3 = st.columns(3)

# NIVEL Y EXP
with col1:
    st.markdown("### 🧬 Nivel")
    st.metric("Nivel actual", final_stats["level"])
    exp_pct = int((final_stats["exp"] / final_stats["exp_to_next_level"]) * 100)
    st.progress(exp_pct)

# ENERGÍA
with col2:
    st.markdown("### ⚡ Energía")
    st.metric("Energía", final_stats["energy"])
    st.progress(int((final_stats["energy"] / final_stats["max_energy"]) * 100))

# BOSS
with col3:
    st.markdown("### 👹 Boss del Mes")

    boss_data = bosses.get_current_boss()

    # Si NO hay boss, mostramos algo visual pero seguro
    if not boss_data:
        st.write("🟣 **No hay Boss activo este mes.**")
        st.progress(0)
    else:
        name = boss_data.get("name", "Boss desconocido")
        phase = boss_data.get("phase", "?")
        hp = boss_data.get("current_hp", 0)

        st.write(f"**{name} — Fase {phase}**")
        st.progress(int((hp / 100) * 100))


# -----------------------------------------------------------
# STATS VS STATS FINALES
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## ⚔️ Estadísticas Finales (con buffs/debuffs)")

stat_cols = st.columns(6)

stat_names = ["strength", "intelligence", "wisdom", "charisma", "dexterity", "luck"]
pretty_names = ["Fuerza", "Inteligencia", "Sabiduría", "Carisma", "Destreza", "Suerte"]

for idx, stat in enumerate(stat_names):
    base = base_stats[stat]
    final = final_stats[stat]
    diff = final - base

    color = "white"
    if diff > 0:
        color = "#7CFF7C"
    elif diff < 0:
        color = "#FF7C7C"

    with stat_cols[idx]:
        st.markdown(
            f"""
            <div style='color:{color}; font-size:20px;'>
                <b>{pretty_names[idx]}</b><br>
                Base: {base}<br>
                Final: {final}<br>
                <i>{'+' if diff>0 else ''}{diff}</i>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------------------------------------
# ESTADO EMOCIONAL
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🧠 Estado Emocional")

emotion = stats.data.get("emotion", {})

emo_cols = st.columns(6)

for idx, (key, value) in enumerate(emotion.items()):
    if key == "notes":
        continue

    color = "#A8C0FF"
    # Asegurar que value sea un número
    try:
        val = float(value)
    except:
        val = 50  # valor neutral por defecto
    
    if value > 70:
        color = "#FF7C7C"
    elif value < 30:
        color = "#7CFF7C"
    else:
        color = "#A8C0FF"

    with emo_cols[idx % 6]:
        st.metric(label=key.capitalize(), value=value)

# -----------------------------------------------------------
# MISIONES ACTIVAS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📅 Misiones Activas del Día")

daily_missions = stats.data["missions"]["daily"]

for i, m in enumerate(daily_missions):
    with st.expander(f"{m['title']} — {m['reward_exp']} XP"):
        st.write(m["description"])
        st.write(f"**Deadline:** {m['deadline']}")
        st.write(f"**Dificultad:** {m['difficulty']}")

        if st.button(f"✔ Completar misión {i}"):
            missions.complete_mission("daily", i)
            st.success("¡Misión completada!")
            st.experimental_rerun()

# -----------------------------------------------------------
# MAPA DEL MUNDO
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🌍 Reinos del Mundo")

realms = stats.data["world"]["realms"]

cols_world = st.columns(3)

index = 0
for realm, info in realms.items():
    with cols_world[index % 3]:
        st.subheader(realm.capitalize())
        st.progress(info["progress"])
        st.write(f"Reputación: **{info['reputation']}**")
        st.write(f"Dificultad: {info['difficulty']}/5")
    index += 1

# -----------------------------------------------------------
# EVENTOS RECIENTES
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 📜 Eventos Recientes")

events = stats.data.get("events", [])

for ev in events[-5:]:
    st.write(f"**[{ev['date']}]** {ev.get('description', ev.get('name', 'Evento'))}")

# -----------------------------------------------------------
# MEMORIA / BACKUPS
# -----------------------------------------------------------
st.markdown("---")
st.markdown("## 🗃️ Memoria del Sistema")

latest_backup = memory.auto_backup()
st.write(latest_backup)

if st.button("Crear Backup Manual"):
    memory.manual_backup("manual_backup")
    st.success("Backup manual creado.")

st.markdown("---")
st.markdown("### 🧙 Fin del HUD de Aureon Nightweaver")
