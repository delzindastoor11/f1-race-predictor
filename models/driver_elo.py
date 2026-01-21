import pandas as pd
from collections import defaultdict

INITIAL_ELO = 1500
K_FACTOR = 16


def expected_score(ra, rb):
    return 1 / (1 + 10 ** ((rb - ra) / 400))


def compute_driver_elo(results: pd.DataFrame) -> pd.DataFrame:
    """
    Computes PRE-race ELO for each driver in each race.
    Optimized: no nested pandas iteration.
    """

    elo = defaultdict(lambda: INITIAL_ELO)
    records = []

    # Ensure deterministic race order
    results = results.sort_values(["race_id", "position_order"])

    for race_id, race_df in results.groupby("race_id"):
        # Extract finished drivers only
        finished = race_df[race_df["status_id"] == 1]

        drivers = finished["driver_id"].tolist()

        # Record PRE-race ELO
        for d in drivers:
            records.append({
                "race_id": race_id,
                "driver_id": d,
                "driver_elo": elo[d],
            })

        # Update ELO AFTER race
        for i in range(len(drivers)):
            di = drivers[i]
            ri = elo[di]

            for j in range(i + 1, len(drivers)):
                dj = drivers[j]
                rj = elo[dj]

                ei = expected_score(ri, rj)

                # di finished ahead of dj
                elo[di] += K_FACTOR * (1 - ei)
                elo[dj] += K_FACTOR * (0 - (1 - ei))

    return pd.DataFrame(records)
