from fastapi import FastAPI
from app.api.v1 import health, auth
from app.core.firebase import init_firebase

init_firebase()

app = FastAPI(title="SafeCheck API")

@app.get("/health")
def root_health_check():
    return {"status": "ok", "message": "Healthy"}

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
