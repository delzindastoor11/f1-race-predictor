import numpy as np
import pandas as pd

def simulate_race(
    grid_df: pd.DataFrame,
    circuit,
    scenario: dict,
    n_simulations: int = 5000,
):
    drivers = grid_df.copy()
    N = len(drivers)

    results = {
        d: {"wins": 0, "podiums": 0, "dnf": 0, "positions": []}
        for d in drivers["driver_id"]
    }

    for _ in range(n_simulations):
        pace = (
            drivers["driver_elo"] * 0.45 +
            (1 / drivers["constructor_pace_index"]) * 600 +
            np.random.normal(0, 50, N)
        )

        pace *= circuit.quali_weight

        # DNFs
        dnf_prob = (
            (1 - drivers["constructor_reliability"]) *
            scenario["mechanical"]["reliability_multiplier"]
        )

        dnfs = np.random.rand(N) < dnf_prob
        order = np.argsort(-pace)

        finishing_order = []
        for i in order:
            if dnfs.iloc[i]:
                results[drivers.iloc[i]["driver_id"]]["dnf"] += 1
            else:
                finishing_order.append(i)

        for pos, idx in enumerate(finishing_order):
            did = drivers.iloc[idx]["driver_id"]
            results[did]["positions"].append(pos + 1)
            if pos == 0:
                results[did]["wins"] += 1
            if pos < 3:
                results[did]["podiums"] += 1

    summary = []
    for did, r in results.items():
        summary.append({
            "driver_id": did,
            "win_prob": r["wins"] / n_simulations,
            "podium_prob": r["podiums"] / n_simulations,
            "dnf_prob": r["dnf"] / n_simulations,
            "avg_finish": (
                np.mean(r["positions"]) if r["positions"] else None
            )
        })

    return pd.DataFrame(summary).sort_values("win_prob", ascending=False)
