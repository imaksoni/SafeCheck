import os
import json
import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

def init_firebase():
    if not firebase_admin._apps:
        # Check if we have credentials passed in config (e.g., JSON string)
        if settings.FIREBASE_CREDENTIALS:
            try:
                cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                return
            except Exception as e:
                print(f"Failed to initialize Firebase with FIREBASE_CREDENTIALS: {e}")

        # Fallback to default application credentials if GOOGLE_APPLICATION_CREDENTIALS is set
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
            return

        print("Warning: Firebase initialized without credentials (using default). This may fail in production.")
        firebase_admin.initialize_app()
