import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

def load_driver_lookup():
    drivers = pd.read_csv(RAW / "drivers.csv")
    drivers["driver_name"] = drivers["forename"] + " " + drivers["surname"]
    return drivers[["driverId", "driver_name"]].rename(
        columns={"driverId": "driver_id"}
    )

def load_constructor_lookup():
    constructors = pd.read_csv(RAW / "constructors.csv")
    return constructors[["constructorId", "name"]].rename(
        columns={
            "constructorId": "constructor_id",
            "name": "constructor_name",
        }
    )
