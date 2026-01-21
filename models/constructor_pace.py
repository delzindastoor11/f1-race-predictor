import pandas as pd

def compute_constructor_pace(
    dataset: pd.DataFrame,
    window: int = 5,
) -> pd.DataFrame:
    """
    Compute rolling constructor pace index.
    Lower = faster team.

    Uses ONLY races prior to the current one.
    One value per constructor per race.
    """

    required_cols = {
        "season",
        "round",
        "race_id",
        "constructor_id",
        "position_order",
    }

    if not required_cols.issubset(dataset.columns):
        raise RuntimeError("Dataset missing required columns for constructor pace")

    df = dataset.copy()

    # Sort strictly by time
    df = df.sort_values(
        ["season", "round", "position_order"]
    ).reset_index(drop=True)

    results = []

    # Process per constructor
    for constructor_id, group in df.groupby("constructor_id"):

        group = group.sort_values(
            ["season", "round", "position_order"]
        )

        history = []

        # 🔑 iterate per race, not per driver row
        for race_id, race_group in group.groupby("race_id", sort=False):

            # Compute pace using ONLY past races
            if len(history) > 0:
                pace = pd.Series(history).median()
            else:
                pace = None

            results.append({
                "race_id": race_id,
                "constructor_id": constructor_id,
                "constructor_pace_index": pace,
            })

            # 🔑 update history AFTER computing pace
            # Use median finish of the team in this race
            race_median_finish = race_group["position_order"].median()
            history.append(race_median_finish)

            # Keep rolling window bounded
            if len(history) > window:
                history = history[-window:]

    pace_df = pd.DataFrame(results)

    return pace_df
