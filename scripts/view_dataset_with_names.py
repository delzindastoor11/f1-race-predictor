import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

# Load processed dataset
df = pd.read_csv(PROCESSED / "dataset_pre_quali.csv")

# Load lookup tables
drivers = pd.read_csv(RAW / "drivers.csv")
constructors = pd.read_csv(RAW / "constructors.csv")
circuits = pd.read_csv(RAW / "circuits.csv")

# Build readable names
drivers["driver_name"] = drivers["forename"] + " " + drivers["surname"]

# Merge names (LEFT joins — never drop rows)
df = df.merge(
    drivers[["driverId", "driver_name"]],
    how="left",
    left_on="driver_id",
    right_on="driverId",
)

df = df.merge(
    constructors[["constructorId", "name"]],
    how="left",
    left_on="constructor_id",
    right_on="constructorId",
)

df = df.merge(
    circuits[["circuitId", "name"]],
    how="left",
    left_on="circuit_id",
    right_on="circuitId",
    suffixes=("", "_circuit"),
)

# Rename for clarity
df = df.rename(columns={
    "name": "constructor_name",
    "name_circuit": "circuit_name",
})

# Select a clean view
view_cols = [
    "season",
    "round",
    "driver_name",
    "constructor_name",
    "circuit_name",
    "driver_elo",
    "constructor_pace_index",
    "constructor_reliability",
    "driver_dnf_rate_mech",
]

print(df[view_cols].dropna().head(20))

