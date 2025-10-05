from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, json, numpy as np

app = FastAPI()

# ✅ Enable CORS for all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Handle OPTIONS preflight requests
@app.options("/{rest_of_path:path}")
async def preflight(rest_of_path: str):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return JSONResponse(status_code=200, content={}, headers=headers)

# ✅ Load telemetry data safely
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
try:
    with open(file_path, "r") as f:
        telemetry = json.load(f)
except Exception as e:
    print("ERROR >>> could not load JSON file:", repr(e))
    telemetry = []

# ✅ POST endpoint with detailed error capture
@app.post("/")
async def get_latency_metrics(request: Request):
    try:
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

        headers = {"Access-Control-Allow-Origin": "*"}
        return JSONResponse(status_code=200, content={"results": results}, headers=headers)

    except Exception as e:
        # ✅ Print error to logs and return readable JSON message
        print("ERROR >>>", repr(e))
        headers = {"Access-Control-Allow-Origin": "*"}
        return JSONResponse(status_code=500, content={"error": str(e)}, headers=headers)
