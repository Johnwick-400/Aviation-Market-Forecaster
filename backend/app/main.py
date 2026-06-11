import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Aviation Market Forecaster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Absolute path to the processed parquet, resolved from this file's location so
# the API works regardless of the working directory it is launched from.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARQUET_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "route_demand.parquet")

# The TimesFM model is heavy (downloads a ~200M checkpoint and compiles on first
# use), so we load it lazily on the first forecast request rather than at import
# time. This keeps startup fast and the API responsive to the health check.
forecaster = None

def get_forecaster():
    """Lazily initialise and cache the TimesFM forecaster."""
    global forecaster
    if forecaster is None:
        from ml_pipeline.forecaster import AviationForecaster
        f = AviationForecaster()
        f.load_model()
        forecaster = f
    return forecaster

@app.get("/")
def read_root():
    return {"status": "online", "model": "TimesFM", "version": "1.0.0"}

@app.get("/forecast/{origin}/{dest}")
def get_route_forecast(origin: str, dest: str):
    """
    Returns the 24-month TimesFM demand forecast (median + P10/P90 band) for a
    given origin-destination route, computed from real BTS T-100 history.
    """
    origin, dest = origin.upper(), dest.upper()
    try:
        fc = get_forecaster()
        return fc.forecast_route(origin, dest, parquet_path=PARQUET_PATH)
    except ValueError as e:
        # No historical data for this route — return 404 with a clear message.
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Dataset not built: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
