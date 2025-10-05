from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

import os
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
        from numpy import mean, percentile
        results.append({
            "region": region,
            "avg_latency": round(mean(latencies), 2),
            "p95_latency": round(percentile(latencies, 95), 2),
            "avg_uptime": round(mean(uptimes), 3),
            "breaches": sum(1 for l in latencies if l > threshold)
        })
    return {"results": results}
