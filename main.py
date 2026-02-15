from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uuid
from datetime import datetime

app = FastAPI(title="Sentron Alpha - Full Command Center")

# --- DATABASE & CONFIG ---
USER_REGISTRY = {"Elon Musk": {"level": 3, "secret_key": "ALPHA_9"}}
SYSTEM_CONFIG = {"daily_limit": 10000000, "is_locked": False}
SECURITY_LOGS = []
PENDING_TRANSFERS = {}

class TransferRequest(BaseModel):
    client_name: str
    amount: float
    memo: str

def log_event(user, event_type, detail, status):
    entry = {
        "id": str(uuid.uuid4())[:8],
        "time": datetime.now().strftime("%H:%M:%S"),
        "user": user,
        "event": event_type,
        "detail": detail,
        "status": status
    }
    SECURITY_LOGS.append(entry)

# --- 1. THE VAULT (Verify Transfer) ---
@app.post("/verify-transfer", tags=["Vault Operations"])
async def verify_transfer(data: TransferRequest):
    if SYSTEM_CONFIG["is_locked"]:
        raise HTTPException(status_code=503, detail="VAULT LOCKED DOWN")
    
    if data.amount > SYSTEM_CONFIG["daily_limit"]:
        tx_id = str(uuid.uuid4())[:8]
        PENDING_TRANSFERS[tx_id] = data
        log_event(data.client_name, "LIMIT_EXCEEDED", f"Requested ${data.amount}", "PENDING")
        return {"status": "PENDING", "auth_code": tx_id}

    log_event(data.client_name, "TRANSFER", f"Sent ${data.amount}", "SUCCESS")
    return {"status": "APPROVED"}

# --- 2. THE MANAGER (Pending & Decisions) ---
@app.get("/view-pending", tags=["Admin Manager"])
async def view_pending():
    return {"queue": PENDING_TRANSFERS}

@app.post("/admin-decision", tags=["Admin Manager"])
async def admin_decision(auth_code: str, action: str, admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Invalid Admin Key")
    return {"message": f"Transaction {auth_code} {action}ed"}

# --- 3. THE SECURITY (Logs & Reset) ---
@app.get("/audit-logs", tags=["Security Console"])
async def get_logs(admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Access Denied")
    return SECURITY_LOGS

@app.post("/system-reset", tags=["Security Console"])
async def system_reset(admin_key: str):
    if admin_key == "BLUE_PHOENIX_REBIRTH":
        SYSTEM_CONFIG["is_locked"] = False
        return {"message": "System Unlocked. Phoenix has Risen."}
    raise HTTPException(status_code=401, detail="Wrong Key")

