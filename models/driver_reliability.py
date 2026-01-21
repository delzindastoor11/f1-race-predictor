import pandas as pd

MECHANICAL_KEYWORDS = [
    "engine", "gearbox", "transmission", "clutch",
    "hydraulics", "electrical", "oil", "water",
    "fuel", "battery", "power unit", "driveshaft",
    "brakes", "suspension", "overheating", "tyre",
]

def compute_driver_dnf_rate_mech(
    dataset: pd.DataFrame,
    status_df: pd.DataFrame,
    window: int = 10,
) -> pd.DataFrame:
    """
    Rolling driver mechanical DNF rate.
    Higher = more failure-prone.

    Uses ONLY prior races.
    One value per driver per race.
    """

    required_cols = {
        "race_id",
        "season",
        "round",
        "driver_id",
        "status_id",
    }

    if not required_cols.issubset(dataset.columns):
        raise RuntimeError("Dataset missing required columns")

    if not {"statusId", "status"}.issubset(status_df.columns):
        raise RuntimeError("status.csv missing required columns")

    df = dataset.merge(
        status_df,
        how="left",
        left_on="status_id",
        right_on="statusId",
    )

    df = df.sort_values(["season", "round"]).reset_index(drop=True)

    def is_mechanical_failure(status_text: str) -> int:
        if not isinstance(status_text, str):
            return 0
        s = status_text.lower()
        return int(any(k in s for k in MECHANICAL_KEYWORDS))

    df["mechanical_failure"] = df["status"].apply(is_mechanical_failure)

    results = []

    for driver_id, group in df.groupby("driver_id"):

        history = []

        for race_id, race_group in group.groupby("race_id", sort=False):

            if len(history) > 0:
                rate = sum(history) / len(history)
            else:
                rate = None

            results.append({
                "race_id": race_id,
                "driver_id": driver_id,
                "driver_dnf_rate_mech": rate,
            })

            # Update AFTER computing
            race_failed = int(race_group["mechanical_failure"].any())
            history.append(race_failed)

            if len(history) > window:
                history = history[-window:]

    return pd.DataFrame(results)
