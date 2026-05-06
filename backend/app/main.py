from fastapi import FastAPI
from app.api.v1 import health

app = FastAPI(title="SafeCheck API")

@app.get("/health")
def root_health_check():
    return {"status": "ok", "message": "Healthy"}

app.include_router(health.router, prefix="/api/v1")
