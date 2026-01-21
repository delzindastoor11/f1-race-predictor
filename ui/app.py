import sys
from pathlib import Path

# -----------------------------
# Project path
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

# -----------------------------
# LOAD CSS
# -----------------------------
def load_css():
    css_path = Path("ui/assets/style.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -----------------------------
# IMPORTS
# -----------------------------
from scripts.view_simulation_with_names import simulate_with_names
from simulation.grid import list_all_drivers, list_active_drivers
from simulation.circuit_registry import CIRCUIT_PROFILES
from data.metadata import load_driver_lookup

# -----------------------------
# TEAM GLOW MAPPING
# -----------------------------
def get_team_glow(constructor_name: str) -> str:
    name = constructor_name.lower()

    if "red bull" in name:
        return "glow-red-bull"
    if "ferrari" in name:
        return "glow-ferrari"
    if "mercedes" in name:
        return "glow-mercedes"
    if "mclaren" in name:
        return "glow-mclaren"
    if "aston" in name:
        return "glow-aston-martin"
    if "alpine" in name:
        return "glow-alpine"
    if "williams" in name:
        return "glow-williams"

    return "glow-default"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_dataset():
    return pd.read_csv("data/processed/dataset_pre_quali.csv")

df = load_dataset()
drivers_lookup = load_driver_lookup()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🏎️ Race Configuration")

season = st.sidebar.selectbox(
    "Season",
    sorted(df["season"].dropna().unique().astype(int)),
)

round_ = st.sidebar.selectbox(
    "Round",
    sorted(df[df["season"] == season]["round"].unique().astype(int)),
)

circuit_id = st.sidebar.selectbox(
    "Circuit",
    options=list(CIRCUIT_PROFILES.keys()),
    format_func=lambda cid: CIRCUIT_PROFILES[cid].name,
)

grid_mode = st.sidebar.radio(
    "Driver Selection",
    ["Active grid only", "Custom selection"],
)

if grid_mode == "Active grid only":
    selected_drivers = list_active_drivers(df, season)
else:
    all_drivers = list_all_drivers(df)
    driver_names = drivers_lookup.set_index("driver_id")["driver_name"].to_dict()

    selected_drivers = st.sidebar.multiselect(
        "Select drivers",
        options=all_drivers,
        format_func=lambda d: driver_names.get(d, f"Driver {d}"),
        default=list_active_drivers(df, season),
    )

# -----------------------------
# CONDITIONS
# -----------------------------
st.sidebar.markdown("### 🌦️ Conditions")

rain_prob = st.sidebar.slider("Rain probability", 0.0, 1.0, 0.3)
reliability_mult = st.sidebar.slider("Mechanical unreliability", 0.5, 2.0, 1.0)
chaos_mult = st.sidebar.slider("Accident chaos", 0.5, 2.0, 1.0)

n_simulations = st.sidebar.slider(
    "Monte Carlo runs",
    1000, 10000, 3000, step=500
)

scenario = {
    "weather": {"rain_prob": rain_prob},
    "mechanical": {"reliability_multiplier": reliability_mult},
    "chaos": {"accident_multiplier": chaos_mult},
}

# -----------------------------
# MAIN PANEL
# -----------------------------
st.title("🏁 Formula 1 Race Predictor")

st.markdown(
    f"**Season {season}, Round {round_} — "
    f"{CIRCUIT_PROFILES[circuit_id].name}**"
)

# -----------------------------
# RUN SIMULATION
# -----------------------------
if st.button("🚦 Run Simulation"):
    with st.spinner("Simulating race..."):
        result = simulate_with_names(
            dataset=df,
            season=season,
            round=round_,
            circuit_id=circuit_id,
            scenario=scenario,
            selected_drivers=selected_drivers,
            n_simulations=n_simulations,
        )

    st.success("Simulation complete")

    # -----------------------------
    # WINNER CARD
    # -----------------------------
    winner = result.iloc[0]
    glow_class = get_team_glow(winner["constructor_name"])

    driver_img = (
        winner["driver_name"]
        .lower()
        .replace(" ", "_")
        + ".png"
    )

    img_path = Path("ui/assets/drivers") / driver_img
    if not img_path.exists():
        img_path = "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"

    st.markdown(
        f"""
        <div class="winner-card {glow_class}">
            <img src="{img_path}" class="winner-img">
            <div class="winner-text">
                <h2>🏆 Predicted Winner</h2>
                <h3>{winner['driver_name']}</h3>
                <p>{winner['constructor_name']}</p>
                <p><b>Win Probability:</b> {winner['win_prob']:.1%}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------
    # FULL RESULTS TABLE
    # -----------------------------
    st.dataframe(
        result.style.format({
            "win_prob": "{:.1%}",
            "podium_prob": "{:.1%}",
            "avg_finish": "{:.2f}",
            "dnf_prob": "{:.1%}",
        }),
        use_container_width=True,
    )

    st.caption("Developed by Delzin Dastoor")
