from dataclasses import dataclass

@dataclass
class CircuitProfile:
    circuit_id: int
    name: str

    # Race dynamics
    overtake_difficulty: float
    safety_car_rate: float
    accident_multiplier: float
    pit_loss_seconds: float

    # Car sensitivity
    power_sensitivity: float
    aero_sensitivity: float
    tyre_deg_rate: float

    # Importance of qualifying
    quali_weight: float
