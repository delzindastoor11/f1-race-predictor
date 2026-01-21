import pandas as pd

from data.metadata import (
    load_driver_lookup,
    load_constructor_lookup,
)
from simulation.simulator import run_race_simulation


def simulate_with_names(
    dataset: pd.DataFrame,
    season: int,
    round: int,
    circuit_id: int,
    scenario: dict,
    selected_drivers=None,
    n_simulations: int = 5000,
):
    # -----------------------------
    # Run simulation (IDs only)
    # -----------------------------
    result = run_race_simulation(
        dataset=dataset,
        season=season,
        round=round,
        circuit_id=circuit_id,
        scenario=scenario,
        selected_drivers=selected_drivers,
        n_simulations=n_simulations,
    )

    # -----------------------------
    # Build GRID-LOCKED mapping
    # -----------------------------
    grid = dataset[
        (dataset["season"] == season) &
        (dataset["round"] == round)
    ][["driver_id", "constructor_id"]].drop_duplicates()

    # -----------------------------
    # Load metadata
    # -----------------------------
    drivers = load_driver_lookup()
    constructors = load_constructor_lookup()

    # -----------------------------
    # Attach names (SAFE JOINS)
    # -----------------------------
    result = result.merge(drivers, on="driver_id", how="left")
    result = result.merge(grid, on="driver_id", how="left")
    result = result.merge(constructors, on="constructor_id", how="left")

    # -----------------------------
    # Final presentation
    # -----------------------------
    cols = [
        "driver_name",
        "constructor_name",
        "win_prob",
        "podium_prob",
        "avg_finish",
        "dnf_prob",
    ]

    return (
        result[cols]
        .sort_values("win_prob", ascending=False)
        .reset_index(drop=True)
    )
