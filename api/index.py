from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json, os, numpy as np

app = FastAPI()

# ✅ Enable CORS for all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Use correct JSON path
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(file_path, "r") as f:
    telemetry = json.load(f)


@app.post("/")
async def get_latency_metrics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 0)

    results = []
    for region in regions:
        region_data = [r for r in telemetry if r["region"] == region]
        if not region_data:
            continue
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for l in latencies if l > threshold)

        results.append({
            "region": region,
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": breaches
        })
    return {"results": results}
