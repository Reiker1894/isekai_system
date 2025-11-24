import streamlit as st
from modules.stats import StatsManager
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Administración del Sistema — Aureon",
    layout="wide"
)

stats = StatsManager()
effects = stats.active_effects()
curse = stats.data.get("curse", {})

# ----------------------------------------------
# CSS estilo Solo Leveling
# ----------------------------------------------
st.markdown("""
<style>
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

    .curse-icon {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: radial-gradient(circle, #B35CFF 0%, #6D1FBF 70%);
        animation: pulse_purple 2.2s infinite;
        display: inline-block;
        margin-right: 10px;
    }

    @keyframes pulse_purple {
        0% { box-shadow: 0 0 10px #7B2FFF; }
        50% { box-shadow: 0 0 25px #B35CFF; }
        100% { box-shadow: 0 0 10px #7B2FFF; }
    }

</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#A8C0FF;'>⚙️ Administración del Sistema Isekai</h1>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================================
# SECTION 1 — EFECTOS ACTIVOS
# ==========================================================
st.markdown("<div class='sl-title'>✨ Efectos Activos</div>", unsafe_allow_html=True)

if len(effects) == 0:
    st.info("No hay efectos activos.")
else:
    for e in effects:
        effect_class = "buff" if e["type"] == "buff" else "debuff"
        st.markdown(f"""
            <div class="effect-card {effect_class}">
                <strong style="color:white;">{e['name']}</strong><br>
                <span style="color:#A8C0FF;">Tipo: {e['type']}</span><br>
                <span style="color:#7F8CFF;">Inicia: {e['start_at']}</span><br>
                <span style="color:#7F8CFF;">Expira: {e['expires_at']}</span><br>
                <span style="color:#6F7FFF;">Modificadores: {e['modifiers']}</span>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🗑 Eliminar TODOS los efectos activos"):
        stats.data["effects"] = []
        stats.save_memory()
        st.success("Todos los efectos han sido eliminados.")


st.markdown("---")


# ==========================================================
# SECTION 2 — AÑADIR BUFFS RÁPIDOS
# ==========================================================
st.markdown("<div class='sl-title'>🔥 Añadir Buff Rápido</div>", unsafe_allow_html=True)

buffs = {
    "Claridad Elevada": {"wisdom": 2, "intelligence": 2},
    "Foco del Estratega": {"wisdom": 3, "intelligence": 3},
    "Impulso de Progreso": {"dexterity": 2, "luck": 1},
    "Mente de Acero": {"charisma": 2},
    "Inspiración del Fénix": {"charisma": 2, "wisdom": 1}
}

buff_name = st.selectbox("Selecciona un Buff", list(buffs.keys()))
buff_duration = st.slider("Duración (horas)", 1, 48, 8)

if st.button("➕ Activar Buff"):
    stats.add_effect(buff_name, "buff", buff_duration, buffs[buff_name])
    st.success(f"Buff '{buff_name}' activado.")


st.markdown("---")


# ==========================================================
# SECTION 3 — AÑADIR DEBUFFS RÁPIDOS
# ==========================================================
st.markdown("<div class='sl-title'>🌑 Añadir Debuff Rápido</div>", unsafe_allow_html=True)

debuffs = {
    "Fatiga Crónica": {"wisdom": -2, "strength": -2},
    "Niebla Mental": {"intelligence": -3},
    "Drenaje Emocional": {"charisma": -2},
    "Carga del Mundo": {"wisdom": -2, "charisma": -1}
}

debuff_name = st.selectbox("Selecciona un Debuff", list(debuffs.keys()))
debuff_duration = st.slider("Duración (horas)", 1, 48, 12)

if st.button("➕ Activar Debuff"):
    stats.add_effect(debuff_name, "debuff", debuff_duration, debuffs[debuff_name])
    st.error(f"Debuff '{debuff_name}' activado.")


st.markdown("---")


# ==========================================================
# SECTION 4 — ACTIVAR MANUALMENTE EL BESO DE LA BRUJA
# ==========================================================
st.markdown("<div class='sl-title'>🩸 Activar Beso de la Bruja (Manual)</div>", unsafe_allow_html=True)

if st.button("⚠️ Forzar Activación de la Maldición"):
    stats.trigger_curse()
    st.error("La Maldición 'Beso de la Bruja' ha sido activada manualmente.")


st.markdown("---")


# ==========================================================
# SECTION 5 — CREAR EFECTO PERSONALIZADO
# ==========================================================
st.markdown("<div class='sl-title'>🧪 Crear Efecto Personalizado</div>", unsafe_allow_html=True)

custom_name = st.text_input("Nombre del efecto")
custom_type = st.selectbox("Tipo", ["buff", "debuff"])
custom_duration = st.slider("Duración (horas)", 1, 72, 12)
custom_mods = st.text_area("Modificadores (ejemplo: strength:2, wisdom:-1)")

if st.button("➕ Crear Efecto"):
    try:
        mod_dict = {}
        for pair in custom_mods.split(","):
            stat, value = pair.split(":")
            mod_dict[stat.strip()] = int(value.strip())

        stats.add_effect(custom_name, custom_type, custom_duration, mod_dict)
        st.success("Efecto personalizado creado.")
    except:
        st.error("Error en el formato de modificadores. Usa: stat:valor, stat:valor")

