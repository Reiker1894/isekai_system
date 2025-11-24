import streamlit as st
from modules.stats import StatsManager
import math

st.set_page_config(
    page_title="Stats — Aureon Nightweaver",
    layout="wide"
)

stats = StatsManager()
data = stats.data
emotion = data["emotion"]
base_stats = data["stats"]

# ------------------------------------
# CSS SOLO LEVELING — ORBS, CARDS, HUD
# ------------------------------------
st.markdown("""
<style>

    /* ========== ORB CONTAINER ========== */
    .orb-container {
        width: 160px;
        height: 160px;
        position: relative;
        margin: auto;
        margin-bottom: 20px;
    }

    /* Círculo base */
    .orb-bg {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 4px solid #1A1D2E;
        background-color: #0E101C;
        box-shadow: 0px 0px 25px rgba(80, 100, 255, 0.15);
        position: absolute;
        top: 0;
        left: 0;
    }

    /* Círculo dinámico (valor) */
    .orb-progress {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 4px solid;
        border-color: #4A66FF;
        clip-path: polygon(50% 50%, 0 0, 100% 0);
        transform-origin: center;
        position: absolute;
        top: 0;
        left: 0;
        transition: transform 0.8s ease-out;
    }

    /* Capa brillante */
    .orb-glow {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        position: absolute;
        top: 0;
        left: 0;
        box-shadow: 0 0 20px #4A66FF, inset 0 0 20px #4A66FF;
        opacity: 0.35;
    }

    /* Texto interior */
    .orb-text {
        position: absolute;
        width: 100%;
        top: 50%;
        text-align: center;
        font-size: 24px;
        font-weight: 600;
        color: #A8C0FF;
        transform: translateY(-50%);
    }

    /* Tarjeta estilo Solo Leveling */
    .sl-card {
        background: #141624;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1F2236;
        box-shadow: 0 0 25px rgba(80, 100, 255, 0.08);
        margin-bottom: 20px;
    }

    /* Títulos */
    .sl-title {
        font-size: 26px;
        font-weight: 700;
        color: #7F97FF;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ------------------------------------
# FUNCIÓN PARA CREAR ORB (RPG HUD)
# ------------------------------------
def orb(label, value):
    """Genera un orbe circular estilo Solo Leveling"""

    if value is None:
        value = 50
    try:
        val = int(value)
    except:
        val = 50

    # Conversión a rotación (0–100 → 0–360 grados)
    rotation = (val / 100) * 360

    orb_html = f"""
    <div class="orb-container">
        <div class="orb-bg"></div>
        <div class="orb-progress" style="transform: rotate({rotation}deg);"></div>
        <div class="orb-glow"></div>
        <div class="orb-text">{val}%<br><span style='font-size:16px; color:#6F7FFF;'>{label}</span></div>
    </div>
    """

    st.markdown(orb_html, unsafe_allow_html=True)


# ------------------------------------
# TÍTULO DE PÁGINA
# ------------------------------------
st.markdown("<h1 style='color:#A8C0FF;'>📊 Estadísticas — Aureon Nightweaver</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#7F8CFF; margin-top:-10px;'>El Tejedor de Sombras y Estrategias</h3>", unsafe_allow_html=True)

st.markdown("---")


# ------------------------------------
# ORBES EMOCIONALES — ESTILO RPG
# ------------------------------------
st.markdown("<div class='sl-title'>⚔️ Estado Emocional (HUD RPG)</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    orb("Energía", base_stats["energy"])
    orb("Motivación", emotion["motivation"])
with col2:
    orb("Clariad", emotion["clarity"])
    orb("Ansiedad", emotion["anxiety"])
with col3:
    orb("Estrés", emotion["stress"])
    orb("Fatiga", emotion["fatigue"])

st.markdown("---")


# ------------------------------------
# STATS BASE (mejorados visualmente)
# ------------------------------------
st.markdown("<div class='sl-title'>📘 Atributos Base</div>", unsafe_allow_html=True)

colA, colB = st.columns(2)

with colA:
    st.markdown("<div class='sl-card'>", unsafe_allow_html=True)
    for k, v in base_stats.items():
        if k in ["energy", "max_energy", "exp", "exp_to_next_level"]:
            continue
        st.markdown(f"<p style='color:#A8C0FF; font-size:18px;'>{k.capitalize()}: <span style='color:white;'>{v}</span></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    st.markdown("<div class='sl-card'>", unsafe_allow_html=True)
    st.markdown("<p class='subtext' style='color:#A8C0FF;'>Aquí irán buffs, debuffs y bonificaciones futuras.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------
# AJUSTE EMOCIONAL (FORMULARIO)
# ------------------------------------
st.markdown("<div class='sl-title'>🧠 Ajustar Estado Emocional</div>", unsafe_allow_html=True)

new_emotion = emotion.copy()

for key, value in emotion.items():
    if key in ["mood", "notes"]:
        continue

    try:
        v = int(value)
    except:
        v = 50

    new_emotion[key] = st.slider(
        key.capitalize(), 0, 100, v
    )

new_emotion["mood"] = st.selectbox(
    "Mood actual",
    ["neutral", "stable", "focused", "tired", "overwhelmed"],
    index=["neutral", "stable", "focused", "tired", "overwhelmed"].index(emotion["mood"])
)

new_emotion["notes"] = st.text_area("Notas emocionales", emotion.get("notes", ""))

if st.button("💾 Guardar cambios emocionales"):
    stats.data["emotion"] = new_emotion
    stats.save_memory()
    st.success("Estado emocional actualizado.")
