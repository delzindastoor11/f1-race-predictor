import pandas as pd

def list_all_drivers(dataset: pd.DataFrame):
    return sorted(dataset["driver_id"].unique().tolist())

def list_active_drivers(dataset: pd.DataFrame, season: int):
    df = dataset[dataset["season"] == season]
    return sorted(df["driver_id"].unique().tolist())

def build_starting_grid(
    dataset: pd.DataFrame,
    season: int,
    round: int,
    selected_drivers: list[int] | None = None,
):
    race_df = dataset[
        (dataset["season"] == season) &
        (dataset["round"] == round)
    ].copy()

    if selected_drivers is not None:
        race_df = race_df[race_df["driver_id"].isin(selected_drivers)]

    if race_df.empty:
        raise RuntimeError("No drivers found for selected grid")

    return race_df.reset_index(drop=True)
