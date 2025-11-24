import streamlit as st
from modules.stats import StatsManager

st.set_page_config(
    page_title="Stats — Aureon Nightweaver",
    layout="wide"
)

stats = StatsManager()
data = stats.data
emotion = data["emotion"]
base_stats = {k: v for k, v in data["stats"].items()}

# ------------------------------
# ESTILO GLOBAL
# ------------------------------
st.markdown("""
<style>
    .stat-card {
        background-color: #1B1E2B;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #292d41;
    }
    .stat-title {
        font-size: 22px;
        font-weight: 700;
        color: #A8C0FF;
        margin-bottom: 10px;
    }
    .stat-value {
        color: white;
        font-size: 28px;
        font-weight: 600;
    }
    .subtext {
        color: #A0A6C0;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# TÍTULO GENERAL
# ------------------------------
st.markdown("<h1 style='color:#A8C0FF;'>📊 Estadísticas del Personaje — Aureon Nightweaver</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#7F8CFF; margin-top:-10px;'>El Tejedor de Sombras y Estrategias</h3>", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------
# STATS BASE Y FINALES
# ------------------------------

st.markdown("## ⚔️ Stats Base vs Stats Finales")

col1, col2, col3 = st.columns([1, 1, 1])

# ----------- STATS BASE -----------------
with col1:
    st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
    st.markdown("<div class='stat-title'>Stats Base</div>", unsafe_allow_html=True)
    for k, v in base_stats.items():
        if k in ["energy", "max_energy", "exp", "exp_to_next_level"]:
            continue
        st.markdown(f"<p class='subtext'>{k.capitalize()}</p><p class='stat-value'>{v}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------- STATS FINALES -----------------
# (por ahora igual a base hasta que agreguemos buffs)
with col2:
    st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
    st.markdown("<div class='stat-title'>Stats Finales</div>", unsafe_allow_html=True)
    for k, v in base_stats.items():
        if k in ["energy", "max_energy", "exp", "exp_to_next_level"]:
            continue
        st.markdown(f"<p class='subtext'>{k.capitalize()}</p><p class='stat-value'>{v}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------- DIFERENCIAS (por ahora 0) -----------------
with col3:
    st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
    st.markdown("<div class='stat-title'>Diferencias</div>", unsafe_allow_html=True)
    for k, v in base_stats.items():
        if k in ["energy", "max_energy", "exp", "exp_to_next_level"]:
            continue
        st.markdown(f"<p class='subtext'>{k.capitalize()}</p><p class='stat-value'>0</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------
# ESTADO EMOCIONAL
# ------------------------------

st.markdown("## 🧠 Estado Emocional")

emo_left, emo_right = st.columns([1, 1])

# ----------- PARTE IZQUIERDA -----------------
with emo_left:
    st.markdown("<div class='stat-title'>Valores actuales</div>", unsafe_allow_html=True)
    st.json(emotion)

# ----------- PARTE DERECHA -----------------
with emo_right:
    st.markdown("<div class='stat-title'>Ajustar emociones (por eventos reales)</div>", unsafe_allow_html=True)

    new_emotion = emotion.copy()

    for key, value in emotion.items():

        # Saltar strings
        if key in ["mood", "notes"]:
            continue

        # Convertir valores extraños a números
        try:
            v = int(value)
        except:
            v = 50

        new_emotion[key] = st.slider(
            key.capitalize(),
            0, 100, v
        )

    new_emotion["notes"] = st.text_area("Notas emocionales", emotion.get("notes", ""))
    new_emotion["mood"] = st.selectbox(
        "Mood actual",
        ["neutral", "stable", "tired", "focused", "overwhelmed"],
        index=["neutral", "stable", "tired", "focused", "overwhelmed"].index(emotion.get("mood", "neutral"))
    )

    if st.button("Guardar cambios emocionales"):
        stats.data["emotion"] = new_emotion
        stats.save_memory()
        st.success("Estado emocional actualizado correctamente.")
