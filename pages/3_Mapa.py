import streamlit as st
from modules.domains import DomainManager
from modules.curse import CurseManager  # si lo tienes
import random
import math

st.set_page_config(page_title="Mapa — Sistema Isekai", layout="wide")

dm = DomainManager()
data = dm.data
curse = data.get("curse", {})

# ===========================================================
#  HOLOGRAPHIC SOLO LEVELING CSS — VERSIÓN COMPLETA
# ===========================================================
st.markdown("""
<style>

    body {
        background-color: #0D0F1A;
    }

    .map-container {
        width: 100%;
        height: 700px;
        position: relative;
        margin-top: 30px;
        border: 1px solid #1C2034;
        background: radial-gradient(circle at center, #0D0F1A 40%, #0A0C14 100%);
        overflow: hidden;
    }

    /* HOLOGRAPHIC GRID ---------------------------------*/
    .map-container::before {
        content: "";
        position: absolute;
        width: 200%;
        height: 200%;
        top: -50%;
        left: -50%;
        background-image: 
            linear-gradient(transparent 95%, rgba(80,120,255,0.08) 100%),
            linear-gradient(90deg, transparent 95%, rgba(80,120,255,0.08) 100%);
        background-size: 50px 50px;
        transform: rotate(5deg);
        pointer-events: none;
    }

    /* NEBLINA ------------------------------------------*/
    .map-container::after {
        content: "";
        position: absolute;
        width: 200%;
        height: 200%;
        top: -50%;
        left: -50%;
        background: radial-gradient(circle, rgba(80,120,255,0.15), transparent 70%);
        animation: slowFog 18s linear infinite;
        pointer-events: none;
    }

    @keyframes slowFog {
        0%   { transform: rotate(0deg); opacity: 0.35; }
        50%  { transform: rotate(180deg); opacity: 0.55; }
        100% { transform: rotate(360deg); opacity: 0.35; }
    }

    /* PARTICULAS FLOTANTES ------------------------------*/
    .particle {
        position: absolute;
        width: 6px;
        height: 6px;
        background: rgba(130,150,255,0.9);
        border-radius: 50%;
        box-shadow: 0 0 12px rgba(150,170,255,1);
        animation: floatParticle 6s linear infinite;
        opacity: 0.85;
    }

    @keyframes floatParticle {
        0%   { transform: translateY(0px) translateX(0px); opacity: 0.5; }
        50%  { transform: translateY(-40px) translateX(20px); opacity: 1; }
        100% { transform: translateY(0px) translateX(0px); opacity: 0.5; }
    }

    /* NODOS --------------------------------------------*/
    .node {
        position: absolute;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: #13172A;
        border: 2px solid #2B2F47;
        box-shadow: 0 0 12px rgba(80,120,255,0.3);
        color: #B7C2FF;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.4s ease-out;
    }

    .node:hover {
        box-shadow: 0 0 25px rgba(100,150,255,0.9);
        transform: scale(1.08);
    }

    /* RUNA GIRATORIA -----------------------------------*/
    .node::before {
        content: "";
        position: absolute;
        width: 160px;
        height: 160px;
        border-radius: 50%;
        background: radial-gradient(circle,
                 rgba(120,150,255,0.15),
                 transparent 70%);
        top: -20px;
        left: -20px;
        z-index: -1;
        animation: spinRune 7s linear infinite;
    }

    @keyframes spinRune {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* PULSE (Luz al subir nivel) ------------------------*/
    .pulse {
        animation: pulse 1.7s infinite;
    }

    @keyframes pulse {
        0%   { box-shadow: 0 0 15px rgba(90,130,255,0.4); }
        50%  { box-shadow: 0 0 35px rgba(110,160,255,1); }
        100% { box-shadow: 0 0 15px rgba(90,130,255,0.4); }
    }

    /* SHOCKWAVE ----------------------------------------*/
    .shockwave {
        animation: shock 1.1s ease-out forwards;
    }

    @keyframes shock {
        0% {
            box-shadow: 0 0 0px rgba(140,170,255,0.9);
            transform: scale(1);
        }
        60% {
            box-shadow: 0 0 40px rgba(160,190,255,1);
            transform: scale(1.25);
        }
        100% {
            box-shadow: 0 0 0px rgba(140,170,255,0.3);
            transform: scale(1);
        }
    }

    /* LÍNEAS DE ENERGÍA --------------------------------*/
    .connection {
        position: absolute;
        background: rgba(90,120,255,0.45);
        box-shadow: 0 0 10px rgba(120,150,255,0.7);
    }

    .connection::before {
        content: "";
        position: absolute;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg,
                 transparent, 
                 rgba(140,170,255,0.9), 
                 transparent);
        animation: flow 2.2s linear infinite;
    }

    @keyframes flow {
        0%   { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* MALDICIÓN ----------------------------------------*/
    .curse-glitch {
        animation: curseGlitch 0.25s infinite;
    }

    @keyframes curseGlitch {
        0%   { transform: translate(0px, 0px); filter: hue-rotate(0deg); }
        33%  { transform: translate(2px, -1px); filter: hue-rotate(7deg); }
        66%  { transform: translate(-2px, 1px); filter: hue-rotate(18deg); }
        100% { transform: translate(0px, 0px); filter: hue-rotate(0deg); }
    }

</style>
""", unsafe_allow_html=True)

# ===========================================================
#  TÍTULO
# ===========================================================
st.markdown("""
<h1 style='color:#9BB0FF;'>🌐 Mapa Holográfico del Sistema Isekai</h1>
<h3 style='color:#7887FF; margin-top:-10px;'>Nodos • Conexiones • Desbloqueos • Progresión</h3>
""", unsafe_allow_html=True)

st.markdown("---")


# ===========================================================
#  CONTENEDOR DEL MAPA
# ===========================================================
st.markdown("<div class='map-container'>", unsafe_allow_html=True)

domains = data["domains"]

def glow_class(domain):
    if domains[domain]["level"] >= 3:
        return "pulse"
    return ""


# ===========================================================
# PARTICULAS FLOTANTES
# ===========================================================
for i in range(18):
    px = random.randint(5, 95)
    py = random.randint(5, 95)
    st.markdown(
        f"<div class='particle' style='top:{py}%; left:{px}%;'></div>",
        unsafe_allow_html=True
    )


# ===========================================================
# POSICIONES DE NODOS
# ===========================================================
positions = {
    "academia":   ("50%", "10%"),
    "politics":   ("20%", "40%"),
    "consulting": ("80%", "40%"),
    "finance":    ("50%", "70%"),
    "family":     ("50%", "88%")
}

labels = {
    "academia": "Academia",
    "politics": "Política",
    "consulting": "Consultoría",
    "finance": "Finanzas",
    "family": "Familia"
}


# ===========================================================
# DIBUJAR NODOS
# ===========================================================
for domain, pos in positions.items():
    top, left = pos
    lvl = domains[domain]["level"]

    # Shockwave si acaba de subir nivel (si exp actual es muy baja)
    animation = "shockwave" if domains[domain]["exp"] < 15 else ""

    node_html = f"""
    <div class="node {glow_class(domain)} {animation} {'curse-glitch' if curse.get('active') else ''}"
         style="top:{top}; left:{left};">
         {labels[domain]}<br>
         Nivel {lvl}
    </div>
    """

    st.markdown(node_html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================
# PANEL DE INFORMACIÓN
# ===========================================================
st.markdown("---")
st.subheader("🔎 Explorar Dominio")

selected = st.selectbox(
    "Selecciona un dominio para ver detalles:",
    ["academia", "politics", "consulting", "finance", "family"]
)

dom = domains[selected]

st.markdown(f"""
### 📘 {dom['name']}
**Nivel:** {dom['level']}  
**EXP:** {dom['exp']} / {dom['exp_to_next']}
""")

st.markdown("#### 🎯 Hitos Desbloqueados")
if dom["unlocked"]:
    for u in dom["unlocked"]:
        st.success(f"• {dom['milestones'][u]}")
else:
    st.info("Aún no has desbloqueado hitos en esta área.")

st.markdown("#### 🎯 Objetivos Semanales")
if dom["weekly_dynamic_milestones"]:
    for i, obj in enumerate(dom["weekly_dynamic_milestones"]):
        st.write(f"- {obj['task']} — **{'✔' if obj['completed'] else 'Pendiente'}**")
else:
    st.info("No hay objetivos dinámicos esta semana.")
