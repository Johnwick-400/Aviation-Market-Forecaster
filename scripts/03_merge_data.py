import pandas as pd
import os
import glob
import zipfile
import io

# Resolve paths relative to the project root, regardless of the current working
# directory (this script may be run from scripts/ or from the repo root).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
BTS_YEARS_DIR = os.path.join(RAW_DIR, "bts_years")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def load_bts_years():
    """Read every per-year BTS T-100 zip in data/raw/bts_years/ and concatenate.

    Each zip contains a T_T100_MARKET_ALL_CARRIER.csv with columns
    PASSENGERS, ORIGIN, DEST, YEAR, MONTH (and possibly carrier columns).
    """
    zips = sorted(glob.glob(os.path.join(BTS_YEARS_DIR, "bts_*.zip")))
    if not zips:
        return None

    frames = []
    for zpath in zips:
        with zipfile.ZipFile(zpath) as zf:
            # The data file is the T_T100* CSV (ignore Documentation.csv).
            data_names = [n for n in zf.namelist()
                          if n.lower().endswith(".csv") and "documentation" not in n.lower()]
            if not data_names:
                print(f"  skip {os.path.basename(zpath)}: no data CSV")
                continue
            with zf.open(data_names[0]) as fh:
                df = pd.read_csv(io.BytesIO(fh.read()),
                                 usecols=lambda c: c.upper() in
                                 {"PASSENGERS", "ORIGIN", "DEST", "YEAR", "MONTH"})
        frames.append(df)
        print(f"  loaded {os.path.basename(zpath)}: {len(df):,} rows")

    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def merge_datasets():
    print("Initiating ETL Merge Pipeline (multi-year BTS T-100)...")

    airports_path = os.path.join(RAW_DIR, "openflights_airports.csv")
    if not os.path.exists(airports_path):
        print("Airports metadata missing. Run 01_fetch_openflights.py first.")
        return

    airports_cols = ["AirportID", "Name", "City", "Country", "IATA", "ICAO",
                     "Lat", "Lon", "Alt", "TZ", "DST", "TzDb", "Type", "Source"]
    airports_df = pd.read_csv(airports_path, header=None, names=airports_cols, na_values="\\N")
    airports_df = airports_df[["IATA", "City", "Country", "Lat", "Lon"]].dropna(subset=["IATA"])

    bts_df = load_bts_years()
    if bts_df is None:
        # Fall back to a single legacy bts_t100.csv if present.
        legacy = os.path.join(RAW_DIR, "bts_t100.csv")
        if os.path.exists(legacy):
            print("No year-zips found; using legacy bts_t100.csv")
            bts_df = pd.read_csv(legacy, usecols=lambda c: c.upper() in
                                 {"PASSENGERS", "ORIGIN", "DEST", "YEAR", "MONTH"})
        else:
            print("No BTS data found in data/raw/bts_years/. Nothing to merge.")
            return

    bts_df = bts_df.rename(columns={
        "YEAR": "year", "MONTH": "month", "ORIGIN": "origin",
        "DEST": "dest", "PASSENGERS": "passengers",
    })

    # Build a monthly date and aggregate passenger demand per route per month.
    bts_df["date"] = pd.to_datetime(bts_df.assign(day=1)[["year", "month", "day"]])
    route_demand = (bts_df.groupby(["date", "origin", "dest"])["passengers"]
                    .sum().reset_index())

    # Drop route-months with zero passengers (cargo-only / placeholder rows).
    route_demand = route_demand[route_demand["passengers"] > 0]

    # Join airport metadata for origin and destination.
    route_demand = route_demand.merge(airports_df, left_on="origin", right_on="IATA", how="left")
    route_demand = route_demand.rename(columns={
        "City": "origin_city", "Country": "origin_country",
        "Lat": "origin_lat", "Lon": "origin_lon"}).drop(columns=["IATA"])
    route_demand = route_demand.merge(airports_df, left_on="dest", right_on="IATA", how="left")
    route_demand = route_demand.rename(columns={
        "City": "dest_city", "Country": "dest_country",
        "Lat": "dest_lat", "Lon": "dest_lon"}).drop(columns=["IATA"])

    route_demand = route_demand.sort_values(["origin", "dest", "date"])

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DIR, "route_demand.parquet")
    route_demand.to_parquet(output_path, engine="fastparquet")

    n_routes = route_demand.groupby(["origin", "dest"]).ngroups
    months = route_demand["date"].dt.strftime("%Y-%m")
    print(f"✅ Saved {output_path}")
    print(f"   Shape: {route_demand.shape} | routes: {n_routes:,} | "
          f"date range: {months.min()} → {months.max()}")
    pts = route_demand.groupby(["origin", "dest"]).size()
    print(f"   History per route: median={int(pts.median())} max={int(pts.max())} months")


if __name__ == "__main__":
    merge_datasets()
