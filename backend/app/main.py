from fastapi import FastAPI
from app.api.v1 import health, auth, trusted_contacts, safety_sessions, snapshots
from app.core.firebase import init_firebase

init_firebase()

app = FastAPI(title="SafeCheck API")

@app.get("/health")
def root_health_check():
    return {"status": "ok", "message": "Healthy"}

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(trusted_contacts.router, prefix="/api/v1/trusted-contacts", tags=["trusted-contacts"])
app.include_router(safety_sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(snapshots.router, prefix="/api/v1/snapshots", tags=["snapshots"])
