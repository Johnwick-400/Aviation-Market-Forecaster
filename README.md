# Aviation Market Forecaster

A full-stack application that generates 24-month passenger demand forecasts for airline routes using **Google TimesFM 2.5** — a zero-shot time-series foundation model.

---

## Architecture

```
market-forecaster/
├── backend/          # FastAPI REST API
│   └── app/main.py   # API routes
├── frontend/         # React + Tailwind UI
│   └── src/App.jsx   # Single-page forecast dashboard
├── ml_pipeline/      # TimesFM inference wrapper
│   └── forecaster.py # AviationForecaster class
├── data/             # Parquet route demand data (not committed)
└── docker-compose.yml
```

The frontend calls `GET /forecast/{origin}/{dest}` on the backend, which (when real data is available) uses `AviationForecaster` to run TimesFM inference on historical passenger data and returns a 24-month forecast with P10/P50/P90 confidence intervals.

---

## Prerequisites

- Python 3.10+ with a virtual environment (project uses `myenv/`)
- Node.js 18+
- PyTorch (CPU) — installed automatically via `requirements.txt`

---

## Running Locally

### Backend

```bash
# From the project root, with myenv activated
source myenv/bin/activate
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu

uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm start
```

UI available at `http://localhost:3000`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/forecast/{origin}/{dest}` | 24-month forecast for a route (IATA codes) |

**Example:**
```bash
curl http://localhost:8000/forecast/JFK/LAX
```

---

## Docker

```bash
docker-compose up --build
```

- Backend → `http://localhost:8000`
- Frontend → `http://localhost:3000`

---

## Using Real Data

1. Place a Parquet file at `data/processed/route_demand.parquet` with columns: `origin`, `dest`, `date`, `passengers`.
2. In `backend/app/main.py`, uncomment the `forecaster.forecast_route(...)` call and remove the simulated data block.

The `AviationForecaster` class in `ml_pipeline/forecaster.py` downloads the `google/timesfm-2.5-200m-pytorch` checkpoint from Hugging Face on first run (~800 MB). Set `HF_TOKEN` to avoid rate limits:

```bash
export HF_TOKEN=your_token_here
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | Google TimesFM 2.5 (200M, PyTorch) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18, Recharts, Tailwind CSS, Framer Motion |
| Containerization | Docker + Docker Compose |
