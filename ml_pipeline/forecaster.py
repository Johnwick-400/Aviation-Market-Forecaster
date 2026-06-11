import pandas as pd
import numpy as np
import os
try:
    import timesfm
    from timesfm import ForecastConfig
except ImportError:
    print("Warning: timesfm package not installed. Run: pip install timesfm torch")

class AviationForecaster:
    def __init__(self, context_len=512, horizon_len=24):
        self.context_len = context_len
        self.horizon_len = horizon_len
        self.tfm = None

    def load_model(self):
        print("Initializing Google TimesFM 2.5 model...")
        self.tfm = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
            "google/timesfm-2.5-200m-pytorch"
        )
        self.tfm.compile(ForecastConfig(
            max_context=self.context_len,
            max_horizon=self.horizon_len,
        ))
        print("✅ Model loaded.")

    def forecast_route(self, origin, dest, parquet_path="../data/processed/route_demand.parquet"):
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Data not found at {parquet_path}")

        df = pd.read_parquet(parquet_path)
        route_df = df[(df['origin'] == origin) & (df['dest'] == dest)].copy()

        if route_df.empty:
            raise ValueError(f"No historical data found for route {origin}-{dest}")

        route_df = route_df.sort_values('date')
        historical_demand = route_df['passengers'].values.astype(float)

        if len(historical_demand) > self.context_len:
            historical_demand = historical_demand[-self.context_len:]

        print(f"Generating {self.horizon_len}-month forecast for {origin}-{dest}...")

        # TimesFM 2.5 returns (median_forecast, quantile_forecast).
        # quantile_forecast has shape [batch, horizon, 10] where the last axis is
        # [mean, q0.1, q0.2, ... q0.9]; index 1 = P10, index 5 = P50, index 9 = P90.
        median_forecast, quantile_forecast = self.tfm.forecast(
            horizon=self.horizon_len,
            inputs=[historical_demand],
        )

        predictions = median_forecast[0]
        quantiles = quantile_forecast[0]
        p10 = quantiles[:, 1]
        p90 = quantiles[:, 9]

        last_date = route_df['date'].iloc[-1]
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, self.horizon_len + 1)]

        forecast = []
        for d, med, lo, hi in zip(future_dates, predictions, p10, p90):
            # Demand cannot be negative; clamp the quantile band too.
            med_i = max(0, int(med))
            lo_i = max(0, int(lo))
            hi_i = max(med_i, int(hi))
            forecast.append({
                "date": str(d.date()),
                "predicted_passengers": med_i,
                "p10": min(lo_i, med_i),
                "p90": hi_i,
            })

        return {
            "route": f"{origin}-{dest}",
            "last_historical_date": str(last_date.date()),
            "forecast": forecast,
        }

if __name__ == "__main__":
    # Test execution
    forecaster = AviationForecaster()
    # forecaster.load_model()
    # res = forecaster.forecast_route("JFK", "LAX")
    # print(res)
    print("ML Pipeline Wrapper Ready.")
