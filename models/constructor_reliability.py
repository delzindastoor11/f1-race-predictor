import pandas as pd

# Mechanical failure keywords from Ergast status descriptions
MECHANICAL_KEYWORDS = [
    "engine", "gearbox", "transmission", "clutch",
    "hydraulics", "electrical", "oil", "water",
    "fuel", "battery", "power unit", "driveshaft",
    "brakes", "suspension", "overheating", "tyre",
]

def compute_constructor_reliability(
    dataset: pd.DataFrame,
    status_df: pd.DataFrame,
    window: int = 10,
) -> pd.DataFrame:
    """
    Rolling constructor mechanical reliability score.
    Higher = more reliable.

    Uses ONLY prior races.
    One value per constructor per race.
    """

    required_cols = {
        "race_id",
        "season",
        "round",
        "constructor_id",
        "status_id",
    }

    if not required_cols.issubset(dataset.columns):
        raise RuntimeError("Dataset missing required columns")

    if not {"statusId", "status"}.issubset(status_df.columns):
        raise RuntimeError("status.csv missing required columns")

    # Join status descriptions
    df = dataset.merge(
        status_df,
        how="left",
        left_on="status_id",
        right_on="statusId",
    )

    df = df.sort_values(["season", "round"]).reset_index(drop=True)

    # Classify mechanical failures
    def is_mechanical_failure(status_text: str) -> int:
        if not isinstance(status_text, str):
            return 0
        s = status_text.lower()
        return int(any(k in s for k in MECHANICAL_KEYWORDS))

    df["mechanical_failure"] = df["status"].apply(is_mechanical_failure)

    results = []

    for constructor_id, group in df.groupby("constructor_id"):

        history = []

        for race_id, race_group in group.groupby("race_id", sort=False):

            # Compute reliability using ONLY prior races
            if len(history) > 0:
                failure_rate = sum(history) / len(history)
                reliability = 1.0 - failure_rate
            else:
                reliability = None  # no history yet

            results.append({
                "race_id": race_id,
                "constructor_id": constructor_id,
                "constructor_reliability": reliability,
            })

            # Update history AFTER computing
            # Any mechanical failure in the team this race → failure
            race_failed = int(race_group["mechanical_failure"].any())
            history.append(race_failed)

            if len(history) > window:
                history = history[-window:]

    return pd.DataFrame(results)
