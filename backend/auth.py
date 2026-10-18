import os
import datetime
import jwt
from typing import Optional, Dict

JWT_SECRET = os.environ.get("JWT_SECRET", "apex_rag_super_secret_jwt_key_2026")
JWT_ALGORITHM = "HS256"

DEMO_USERS = {
    "policyholder@apex.com": {
        "password": "password123",
        "name": "Sarah Jenkins",
        "role": "Policyholder",
        "policy_number": "APH-2026-99410",
        "avatar": "SJ"
    },
    "adjuster@apex.com": {
        "password": "password123",
        "name": "David Miller",
        "role": "Claims Adjuster",
        "license_id": "ADJ-CT-88910",
        "avatar": "DM"
    },
    "admin@apex.com": {
        "password": "password123",
        "name": "Elena Rostova",
        "role": "Compliance Officer",
        "avatar": "ER"
    }
}

def create_access_token(user_data: Dict, expires_delta_hours: int = 24) -> str:
    payload = {
        "sub": user_data["email"],
        "name": user_data["name"],
        "role": user_data["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_delta_hours)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[Dict]:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except Exception:
        return None
