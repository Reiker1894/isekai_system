import streamlit as st
from modules.missions import MissionManager
from modules.stats import StatsManager
from datetime import datetime

st.set_page_config(page_title="Recompensas — Aureon Nightweaver", layout="wide")

missions = MissionManager()
stats = StatsManager()
data = missions.data

# -------------------------------------------
# CSS SOLO LEVELING STYLE
# -------------------------------------------
st.markdown("""
<style>

    .reward-card {
        background: #141624;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #24283F;
        box-shadow: 0 0 25px rgba(120, 120, 255, 0.10);
        margin-bottom: 15px;
    }

    .reward-title {
        color: #A9B9FF;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .reward-cost {
        color: #9AA4FF;
        font-size: 16px;
        margin-bottom: 12px;
    }

    .sl-card {
        background: #141624;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #24283F;
        box-shadow: 0 0 20px rgba(120, 120, 255, 0.08);
        margin-bottom: 20px;
    }

    .sl-title {
        font-size: 26px;
        font-weight: 700;
        color: #7F97FF;
        margin-bottom: 15px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<h1 style='color:#9BB0FF;'>🎁 Recompensas — Sistema de Dark Points</h1>
<h3 style='color:#7F88F7; margin-top:-10px;'>El Camino del Esfuerzo debe ser recompensado</h3>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# DARK POINTS PANEL
# ---------------------------------------------------------
dark_points = data.get("dark_points", 0)

st.markdown("<div class='sl-title'>🌑 Tus Dark Points</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sl-card'><h2 style='color:white;'>Saldo: {dark_points} 🌑</h2></div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# TIENDA DE RECOMPENSAS
# ---------------------------------------------------------
st.markdown("<div class='sl-title'>🏪 Tienda de Recompensas</div>", unsafe_allow_html=True)

store = data.get("reward_store", [])

if len(store) == 0:
    st.info("No hay recompensas en la tienda.")
else:
    for idx, reward in enumerate(store):
        with st.container():
            st.markdown("<div class='reward-card'>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='reward-title'>{reward['name']}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='reward-cost'>Coste: {reward['cost']} 🌑</div>",
                unsafe_allow_html=True
            )

            if dark_points >= reward["cost"]:
                if st.button(f"Comprar: {reward['name']}", key=f"buy_{idx}"):
                    # Deduct cost
                    missions.data["dark_points"] -= reward["cost"]

                    # Log the purchase
                    missions.data["logs"].append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "entry": f"Recompensa adquirida: {reward['name']} (-{reward['cost']} Dark Points)"
                    })

                    missions.save_memory()
                    st.success(f"Has comprado: {reward['name']} ⭐")
                    st.experimental_rerun()
            else:
                st.warning("No tienes suficientes Dark Points.")

            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# AÑADIR NUEVA RECOMPENSA
# ---------------------------------------------------------
st.markdown("<div class='sl-title'>➕ Añadir Nueva Recompensa</div>", unsafe_allow_html=True)

new_name = st.text_input("Nombre de la recompensa")
new_cost = st.number_input("Coste en Dark Points", 50, 50000, 300)

if st.button("Agregar a la tienda"):
    missions.data["reward_store"].append({
        "name": new_name,
        "cost": int(new_cost)
    })
    missions.save_memory()
    st.success("Recompensa agregada correctamente.")
    st.experimental_rerun()

# ---------------------------------------------------------
# ELIMINAR RECOMPENSA
# ---------------------------------------------------------
st.markdown("<div class='sl-title'>🗑 Eliminar Recompensa</div>", unsafe_allow_html=True)

if len(store) > 0:
    options = [r["name"] for r in store]
    delete_choice = st.selectbox("Selecciona una recompensa a eliminar", options)

    if st.button("Eliminar"):
        missions.data["reward_store"] = [r for r in store if r["name"] != delete_choice]
        missions.save_memory()
        st.success(f"Recompensa '{delete_choice}' eliminada.")
        st.experimental_rerun()

