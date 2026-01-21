from dataclasses import dataclass, field
from typing import Optional, Dict


# -------------------------------------------------
# CORE RACE CONFIGURATION
# -------------------------------------------------

@dataclass
class RaceConfig:
    """
    Canonical race configuration.
    This is the ONLY object the UI will ever build.
    """

    # -----------------------------
    # RACE IDENTITY
    # -----------------------------
    season: int
    circuit_id: int
    round: Optional[int] = None   # optional (can infer from circuit)

    # -----------------------------
    # WEATHER
    # -----------------------------
    rain_prob: float = 0.0        # 0 → 1
    weather_volatility: float = 0.0

    # -----------------------------
    # CHAOS / INCIDENTS
    # -----------------------------
    accident_multiplier: float = 1.0
    safety_car_multiplier: float = 1.0

    # -----------------------------
    # MECHANICAL STRESS
    # -----------------------------
    reliability_multiplier: float = 1.0

    # -----------------------------
    # STRATEGY / RACE FLOW
    # -----------------------------
    pit_time_variance: float = 1.0
    driver_aggression: float = 0.5   # 0 = conservative, 1 = aggressive

    # -----------------------------
    # SIMULATION CONTROL
    # -----------------------------
    n_simulations: int = 5000
    random_seed: Optional[int] = None


# -------------------------------------------------
# VALIDATION
# -------------------------------------------------

def validate_config(cfg: RaceConfig):
    """
    Hard validation — fail early, fail loud.
    """

    if not (0.0 <= cfg.rain_prob <= 1.0):
        raise ValueError("rain_prob must be between 0 and 1")

    if not (0.0 <= cfg.weather_volatility <= 1.0):
        raise ValueError("weather_volatility must be between 0 and 1")

    if cfg.accident_multiplier <= 0:
        raise ValueError("accident_multiplier must be > 0")

    if cfg.reliability_multiplier <= 0:
        raise ValueError("reliability_multiplier must be > 0")

    if not (0.0 <= cfg.driver_aggression <= 1.0):
        raise ValueError("driver_aggression must be between 0 and 1")

    if cfg.n_simulations < 100:
        raise ValueError("n_simulations too small to be meaningful")


# -------------------------------------------------
# PRESET SCENARIOS (for UI buttons)
# -------------------------------------------------

def preset_dry_normal(season: int, circuit_id: int) -> RaceConfig:
    return RaceConfig(
        season=season,
        circuit_id=circuit_id,
        rain_prob=0.0,
        weather_volatility=0.1,
        accident_multiplier=1.0,
        reliability_multiplier=1.0,
    )


def preset_rain_chaos(season: int, circuit_id: int) -> RaceConfig:
    return RaceConfig(
        season=season,
        circuit_id=circuit_id,
        rain_prob=0.7,
        weather_volatility=0.6,
        accident_multiplier=1.4,
        reliability_multiplier=0.9,
    )


def preset_street_carnage(season: int, circuit_id: int) -> RaceConfig:
    return RaceConfig(
        season=season,
        circuit_id=circuit_id,
        rain_prob=0.3,
        weather_volatility=0.4,
        accident_multiplier=1.6,
        safety_car_multiplier=1.5,
    )
