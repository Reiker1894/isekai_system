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
final_stats = stats.final_stats()
effects = stats.active_effects()
curse = data.get("curse", {})

# ------------------------------------------------------
# CSS SOLO LEVELING HUD + ICONOS ANIMADOS
# ------------------------------------------------------
st.markdown("""
<style>

    /* ORB CONTAINER */
    .orb-container {
        width: 160px;
        height: 160px;
        position: relative;
        margin: auto;
        margin-bottom: 25px;
    }

    .orb-bg {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 4px solid #1A1D2E;
        background-color: #0E101C;
        box-shadow: 0px 0px 25px rgba(80, 100, 255, 0.20);
        position: absolute;
        top: 0;
        left: 0;
    }

    .orb-progress {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 4px solid #4A66FF;
        clip-path: polygon(50% 50%, 0 0, 100% 0);
        transform-origin: center;
        position: absolute;
        top: 0;
        left: 0;
        transition: transform 0.8s ease-out;
    }

    .orb-glow {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 25px #4A66FF, inset 0 0 25px #4A66FF;
        opacity: 0.40;
    }

    .orb-text {
        position: absolute;
        width: 100%;
        top: 50%;
        text-align: center;
        font-size: 22px;
        font-weight: 600;
        color: #A8C0FF;
        transform: translateY(-50%);
    }

    /* SOLO LEVELING CARD */
    .sl-card {
        background: #141624;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #24283F;
        box-shadow: 0 0 25px rgba(80, 100, 255, 0.10);
        margin-bottom: 20px;
    }

    .sl-title {
        font-size: 26px;
        font-weight: 700;
        color: #7F97FF;
        margin-bottom: 15px;
    }

    /* ------------------------------------ */
    /* BUFF / DEBUFF TAGS */
    /* ------------------------------------ */
    .effect-card {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        background: #131521;
        border: 1px solid #2F3250;
        box-shadow: 0 0 18px rgba(100, 120, 255, 0.10);
    }

    .buff {
        border-left: 4px solid #4A77FF;
    }

    .debuff {
        border-left: 4px solid #A840FF;
    }

    /* ICONO ANIMADO MALDICIÓN */
    @keyframes pulse_purple {
        0% { box-shadow: 0 0 10px #7B2FFF; }
        50% { box-shadow: 0 0 25px #B35CFF; }
        100% { box-shadow: 0 0 10px #7B2FFF; }
    }

    .curse-icon {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: radial-gradient(circle, #B35CFF 0%, #6D1FBF 70%);
        animation: pulse_purple 2.2s infinite;
        display: inline-block;
        margin-right: 10px;
    }

    .effect-icon {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #4A66FF;
        opacity: 0.8;
        display: inline-block;
        margin-right: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# ORB FUNCTION
# ------------------------------------------------------
def orb(label, value):
    rotation = (value / 100) * 360
    orb_html = f"""
    <div class="orb-container">
        <div class="orb-bg"></div>
        <div class="orb-progress" style="transform: rotate({rotation}deg);"></div>
        <div class="orb-glow"></div>
        <div class="orb-text">{value}%<br><span style='font-size:15px; color:#7F8CFF;'>{label}</span></div>
    </div>
    """
    st.markdown(orb_html, unsafe_allow_html=True)


# ------------------------------------------------------
# PAGE TITLE
# ------------------------------------------------------
st.markdown("<h1 style='color:#A8C0FF;'>📊 Estadísticas — Aureon Nightweaver</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#7F8CFF;'>Tejedor de Sombras</h3>", unsafe_allow_html=True)
st.markdown("---")


# ------------------------------------------------------
# ORBS
# ------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    orb("Energía", base_stats["energy"])
    orb("Motivación", emotion["motivation"])

with col2:
    orb("Claridad", emotion["clarity"])
    orb("Ansiedad", emotion["anxiety"])

with col3:
    orb("Estrés", emotion["stress"])
    orb("Fatiga", emotion["fatigue"])

st.markdown("---")


# ------------------------------------------------------
# BUFFS & DEBUFFS SECTION
# ------------------------------------------------------
st.markdown("<div class='sl-title'>✨ Efectos Activos (Buffs & Debuffs)</div>", unsafe_allow_html=True)

if len(effects) == 0:
    st.markdown("<p style='color:#7F8CFF;'>No hay efectos activos.</p>", unsafe_allow_html=True)

else:
    for e in effects:
        icon_html = "<div class='effect-icon'></div>" if e["type"] == "buff" else "<div class='curse-icon'></div>"
        effect_class = "buff" if e["type"] == "buff" else "debuff"

        st.markdown(f"""
            <div class="effect-card {effect_class}">
                {icon_html}
                <strong style="color:white;">{e['name']}</strong><br>
                <span style="color:#A8C0FF;">Expira: {e['expires_at']}</span><br>
                <span style="color:#6F7FFF;">Modificadores: {e['modifiers']}</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")


# ------------------------------------------------------
# BASE STATS
# ------------------------------------------------------
st.markdown("<div class='sl-title'>📘 Atributos Base</div>", unsafe_allow_html=True)

st.markdown("<div class='sl-card'>", unsafe_allow_html=True)
for k, v in base_stats.items():
    if k not in ["energy", "max_energy", "exp", "exp_to_next_level"]:
        st.markdown(
            f"<p style='color:#A8C0FF; font-size:18px;'>{k.capitalize()}: "
            f"<span style='color:white;'>{v}</span></p>",
            unsafe_allow_html=True
        )
st.markdown("</div>", unsafe_allow_html=True)
