import streamlit as st
from modules.domains import DomainManager
from modules.curse import CurseManager  # si ya lo tienes
import math

st.set_page_config(page_title="Mapa — Sistema Isekai", layout="wide")

dm = DomainManager()
data = dm.data
curse = data.get("curse", {})

# -----------------------------------------------
# HOLOGRAPHIC SOLO LEVELING CSS
# -----------------------------------------------
st.markdown("""
<style>

    body {
        background-color: #0D0F1A;
    }

    .map-container {
        width: 100%;
        height: 650px;
        position: relative;
        margin-top: 30px;
        border: 1px solid #1C2034;
        background: radial-gradient(circle at center, #0D0F1A 40%, #0A0C14 100%);
        overflow: hidden;
    }

    /* Grid holo */
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

    /* Nodo base */
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

    /* Glow dinámico */
    .node:hover {
        box-shadow: 0 0 25px rgba(100,150,255,0.8);
        transform: scale(1.07);
    }

    .pulse {
        animation: pulse 1.7s infinite;
    }

    @keyframes pulse {
        0%   { box-shadow: 0 0 15px rgba(90,130,255,0.4); }
        50%  { box-shadow: 0 0 30px rgba(110,160,255,0.9); }
        100% { box-shadow: 0 0 15px rgba(90,130,255,0.4); }
    }

    /* Líneas conectando nodos */
    .connection {
        position: absolute;
        background: rgba(90,120,255,0.45);
        box-shadow: 0 0 10px rgba(120,150,255,0.7);
    }

    /* Maldición activa */
    .curse-glitch {
        animation: glitch 1.2s infinite;
    }

    @keyframes glitch {
        0% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(30deg) brightness(1.3); }
        100% { filter: hue-rotate(0deg); }
    }

</style>
""", unsafe_allow_html=True)


# -----------------------------------------------
# PAGE TITLE
# -----------------------------------------------
st.markdown("""
<h1 style='color:#9BB0FF;'>🌐 Mapa Holográfico del Sistema Isekai</h1>
<h3 style='color:#7887FF; margin-top:-10px;'>Nodos • Conexiones • Desbloqueos • Progresión</h3>
""", unsafe_allow_html=True)

st.markdown("---")


# -----------------------------------------------
# MAP LAYOUT
# -----------------------------------------------
st.markdown("<div class='map-container'>", unsafe_allow_html=True)

# Get domain levels for glow intensity
domains = data["domains"]

def glow_class(domain):
    level = domains[domain]["level"]
    return "pulse" if level >= 3 else ""


# ----------------- NODES POSITIONS -----------------
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

# ----------------- DRAW NODES -----------------
for domain, pos in positions.items():
    top, left = pos
    lvl = domains[domain]["level"]

    node_html = f"""
    <div class="node {glow_class(domain)} {'curse-glitch' if curse.get('active') else ''}"
         style="top:{top}; left:{left};">
         {labels[domain]}<br>
         Nivel {lvl}
    </div>
    """
    st.markdown(node_html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------
# CLICK HANDLING (FAKE)
# Streamlit no tiene click nativo sobre HTML, así que usamos selectbox
# -----------------------------------------------
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

