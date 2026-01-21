import pandas as pd

from simulation.grid import build_starting_grid
from simulation.circuit_registry import get_circuit_profile
from simulation.monte_carlo import simulate_race


def run_race_simulation(
    dataset: pd.DataFrame,
    season: int,
    round: int,
    circuit_id: int,
    scenario: dict,
    selected_drivers: list[int] | None = None,
    n_simulations: int = 5000,
):
    """
    High-level race simulation entry point.
    This is what UI / API / CLI should call.
    """

    grid = build_starting_grid(
        dataset=dataset,
        season=season,
        round=round,
        selected_drivers=selected_drivers,
    )

    circuit = get_circuit_profile(circuit_id)

    results = simulate_race(
        grid_df=grid,
        circuit=circuit,
        scenario=scenario,
        n_simulations=n_simulations,
    )

    return results
