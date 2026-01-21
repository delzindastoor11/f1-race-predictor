import pandas as pd
from pathlib import Path
from simulation.circuit_profile import CircuitProfile

RAW = Path("data/raw")

def load_all_circuit_profiles():
    circuits = pd.read_csv(RAW / "circuits.csv")

    profiles = {}

    # -------------------------
    # DEFAULT BASELINE (neutral circuit)
    # -------------------------
    DEFAULT = dict(
        overtake_difficulty=1.0,
        safety_car_rate=0.30,
        accident_multiplier=1.0,
        pit_loss_seconds=22.5,
        power_sensitivity=1.0,
        aero_sensitivity=1.0,
        tyre_deg_rate=1.0,
        quali_weight=0.7,
    )

    for _, row in circuits.iterrows():
        profiles[row["circuitId"]] = CircuitProfile(
            circuit_id=row["circuitId"],
            name=row["name"],
            **DEFAULT,
        )

    # -------------------------
    # REALISTIC OVERRIDES
    # -------------------------
    def override(cid, **kwargs):
        for k, v in kwargs.items():
            setattr(profiles[cid], k, v)

    # Monaco
    override(
        6,
        overtake_difficulty=2.0,
        safety_car_rate=0.75,
        accident_multiplier=1.6,
        pit_loss_seconds=21.0,
        power_sensitivity=0.6,
        aero_sensitivity=1.4,
        tyre_deg_rate=0.8,
        quali_weight=0.9,
    )

    # Monza
    override(
        14,
        overtake_difficulty=0.7,
        power_sensitivity=1.6,
        aero_sensitivity=0.7,
        quali_weight=0.6,
    )

    # Singapore
    override(
        15,
        safety_car_rate=0.80,
        accident_multiplier=1.5,
        tyre_deg_rate=1.4,
        pit_loss_seconds=24.0,
        quali_weight=0.85,
    )

    # Spa
    override(
        13,
        power_sensitivity=1.3,
        aero_sensitivity=1.2,
        safety_car_rate=0.45,
    )

    return profiles


# Global registry
CIRCUIT_PROFILES = load_all_circuit_profiles()

def get_circuit_profile(circuit_id: int) -> CircuitProfile:
    if circuit_id not in CIRCUIT_PROFILES:
        raise RuntimeError(f"Circuit {circuit_id} not found")
    return CIRCUIT_PROFILES[circuit_id]
