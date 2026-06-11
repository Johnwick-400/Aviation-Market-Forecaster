import requests
import os
import pandas as pd

RAW_DIR = "../data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

URLS = {
    "airports": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat",
    "routes": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
}

def fetch_openflights():
    print("Fetching OpenFlights data...")
    for name, url in URLS.items():
        resp = requests.get(url)
        if resp.status_code == 200:
            file_path = os.path.join(RAW_DIR, f"openflights_{name}.csv")
            with open(file_path, "wb") as f:
                f.write(resp.content)
            print(f"✅ Saved {name} to {file_path}")
        else:
            print(f"❌ Failed to fetch {name}: HTTP {resp.status_code}")

if __name__ == "__main__":
    fetch_openflights()
