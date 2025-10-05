from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is alive"}

@app.post("/")
async def echo(request: Request):
    try:
        body = await request.json()
        return JSONResponse(
            status_code=200,
            content={"received": body},
            headers={"Access-Control-Allow-Origin": "*"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": repr(e)},
            headers={"Access-Control-Allow-Origin": "*"},
        )
