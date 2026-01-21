import sys
from pathlib import Path

# -----------------------------
# Ensure project root on path
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from models.driver_elo import compute_driver_elo
from models.constructor_pace import compute_constructor_pace
from models.constructor_reliability import compute_constructor_reliability

# -----------------------------
# CONFIG
# -----------------------------
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")
FEATURE_REGISTRY_PATH = Path("features/feature_registry.csv")

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# LOAD FEATURE REGISTRY
# -----------------------------
registry = pd.read_csv(FEATURE_REGISTRY_PATH)

REQUIRED_COLUMNS = {
    "feature_name",
    "entity",
    "description",
    "source",
    "available_at",
    "valid_for",
    "leakage_risk",
}

if not REQUIRED_COLUMNS.issubset(registry.columns):
    raise RuntimeError("Feature registry schema is invalid")

ALLOWED_TIMINGS = {
    "season_start",
    "pre_weekend",
    "post_qualifying",
    "race_morning",
}

if not set(registry["available_at"]).issubset(ALLOWED_TIMINGS):
    raise RuntimeError("Illegal available_at value in feature registry")

# -----------------------------
# LOAD RAW DATA
# -----------------------------
results = pd.read_csv(RAW_DATA_DIR / "results.csv")
races   = pd.read_csv(RAW_DATA_DIR / "races.csv")
status  = pd.read_csv(RAW_DATA_DIR / "status.csv")

# -----------------------------
# INJECT SEASON / ROUND / META
# -----------------------------
results = results.merge(
    races[["race_id", "season", "round", "race_date", "circuit_id"]],
    how="left",
    on="race_id",
)

# Drop races not present in races.csv
missing = results["season"].isna()
if missing.any():
    bad_ids = results.loc[missing, "race_id"].unique()
    print(
        f"Dropping {len(bad_ids)} races missing from races.csv "
        f"(max race_id={bad_ids.max()})"
    )

results = results.loc[~missing].copy()

# -----------------------------
# CANONICAL DRIVER–RACE DATASET
# -----------------------------
dataset = results.sort_values(
    ["season", "round", "position_order"]
).reset_index(drop=True)

# -----------------------------
# DRIVER ELO (ONCE, CHRONOLOGICAL)
# -----------------------------
driver_elo_df = compute_driver_elo(dataset)

dataset = dataset.merge(
    driver_elo_df,
    how="left",
    on=["race_id", "driver_id"],
)

dataset["driver_elo"] = dataset["driver_elo"].fillna(1500.0)

# -----------------------------
# CONSTRUCTOR PACE (ONCE)
# -----------------------------
constructor_pace_df = compute_constructor_pace(dataset)

dataset = dataset.merge(
    constructor_pace_df,
    how="left",
    on=["race_id", "constructor_id"],
)

# -----------------------------
# CONSTRUCTOR RELIABILITY (ONCE)
# -----------------------------
constructor_reliability_df = compute_constructor_reliability(
    dataset,
    status_df=status,
)

dataset = dataset.merge(
    constructor_reliability_df,
    how="left",
    on=["race_id", "constructor_id"],
)

dataset["constructor_reliability"] = (
    dataset["constructor_reliability"]
    .fillna(1.0)
)

# -----------------------------
# FEATURE COMPUTATION
# -----------------------------
IDENTITY_COLUMNS = {
    "season",
    "round",
    "race_id",
    "driver_id",
    "constructor_id",
    "circuit_id",
    "race_date",
    "position_order",
    "status_id",
}

def compute_feature(feature_name: str, df: pd.DataFrame) -> pd.Series:

    if feature_name in IDENTITY_COLUMNS:
        raise RuntimeError(
            f"Illegal feature '{feature_name}': identity columns are not features"
        )

    # -------------------------
    # REAL FEATURES
    # -------------------------
    if feature_name == "driver_elo":
        return df["driver_elo"]

    if feature_name == "constructor_pace_index":
        return df["constructor_pace_index"]

    if feature_name == "constructor_reliability":
        return df["constructor_reliability"]

    # -------------------------
    # PLACEHOLDERS (INTENTIONAL)
    # -------------------------
    if feature_name.startswith("driver_"):
        return pd.Series(0.0, index=df.index)

    if feature_name.startswith("constructor_"):
        return pd.Series(0.0, index=df.index)

    if feature_name.startswith("quali_"):
        return pd.Series(pd.NA, index=df.index)

    if feature_name.startswith("weather_"):
        return pd.Series(0.0, index=df.index)

    return pd.Series(pd.NA, index=df.index)

# -----------------------------
# BUILD DATASETS BY CONTEXT
# -----------------------------
def build_context_dataset(context: str):
    assert context in {"pre_quali", "post_quali"}

    allowed_features = registry[
        (registry["valid_for"] == "both") |
        (registry["valid_for"] == context)
    ]

    df = dataset.copy()

    for _, row in allowed_features.iterrows():
        fname = row["feature_name"]
        available_at = row["available_at"]

        if context == "pre_quali" and available_at == "post_qualifying":
            raise RuntimeError(
                f"Illegal feature {fname} in pre_quali context"
            )

        df[fname] = compute_feature(fname, df)

    out = PROCESSED_DATA_DIR / f"dataset_{context}.csv"
    df.to_csv(out, index=False)
    print(f"Saved {out}")

# -----------------------------
# EXECUTION
# -----------------------------
if __name__ == "__main__":
    build_context_dataset("pre_quali")
    build_context_dataset("post_quali")
