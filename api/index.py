from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, json, numpy as np

app = FastAPI()

# ✅ Allow every origin and every method
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ✅ Also add an OPTIONS route for pre-flight requests
@app.options("/{rest_of_path:path}")
async def preflight(rest_of_path: str):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return JSONResponse(status_code=200, content={}, headers=headers)

# ---------- existing code ----------
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(file_path, "r") as f:
    telemetry = json.load(f)
