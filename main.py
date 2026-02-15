from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uuid
from datetime import datetime

app = FastAPI(title="Sentron Alpha: Full Security Suite")

# --- 🧠 1. RBAC: THE USER REGISTRY ---
USER_REGISTRY = {
    "Elon Musk": {"level": 3, "secret_key": "ALPHA_9"},
    "Jeff Bezos": {"level": 3, "secret_key": "BLUE_ORIGIN_1"},
    "Duke Dean": {"level": 2, "secret_key": None},
    "Michael": {"level": 1, "secret_key": None}
}

# --- 🤖 2. AI SENTINEL & SYSTEM STATE ---
SYSTEM_CONFIG = {"daily_limit": 10000000, "is_locked": False}
AI_BRAINWASH_WORDS = ["ignore", "previous", "override", "bypass", "admin access"]
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

# --- 🏛️ 3. THE VAULT (The $10M Gate & Sentinel) ---
@app.post("/verify-transfer", tags=["Vault Operations"])
async def verify_transfer(data: TransferRequest):
    # A. AI Sentinel Scan
    memo_lower = data.memo.lower()
    if any(word in memo_lower for word in AI_BRAINWASH_WORDS):
        log_event(data.client_name, "AI_ATTACK", f"Injection detected: {data.memo}", "CRITICAL")
        SYSTEM_CONFIG["is_locked"] = True
        raise HTTPException(status_code=403, detail="AI INTERFERENCE DETECTED - SYSTEM LOCKDOWN")

    if SYSTEM_CONFIG["is_locked"]:
        raise HTTPException(status_code=503, detail="VAULT IS IN LOCKDOWN")

    # B. RBAC & Identity Check
    user = USER_REGISTRY.get(data.client_name)
    if not user:
        log_event(data.client_name, "UNKNOWN_USER", "Denied Access", "FAILED")
        raise HTTPException(status_code=401, detail="Identity Unknown")

    if user["level"] == 3 and data.memo != user["secret_key"]:
        log_event(data.client_name, "INVALID_KEY", "Level 3 Key Mismatch", "DENIED")
        raise HTTPException(status_code=401, detail="Secret Key Required for Level 3")

    # C. The $10M Gate (Pending Stuff)
    if data.amount > SYSTEM_CONFIG["daily_limit"]:
        tx_id = str(uuid.uuid4())[:8]
        PENDING_TRANSFERS[tx_id] = data
        log_event(data.client_name, "LIMIT_EXCEEDED", f"Pending: ${data.amount}", "WAITING")
        return {"status": "PENDING", "auth_code": tx_id, "msg": "Exceeds $10M - Sent to Admin for review"}

    log_event(data.client_name, "TRANSFER", f"Sent ${data.amount}", "SUCCESS")
    return {"status": "APPROVED", "msg": "Transfer successful"}

# --- 🔑 4. SECURITY CONSOLE (Auditor & Phoenix) ---
@app.get("/view-pending", tags=["Admin Manager"])
async def view_pending():
    return {"queue": PENDING_TRANSFERS}

@app.post("/admin-decision", tags=["Admin Manager"])
async def admin_decision(auth_code: str, action: str, admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Invalid Master Key")
    if auth_code not in PENDING_TRANSFERS:
        raise HTTPException(status_code=404, detail="Transaction Not Found")

    tx = PENDING_TRANSFERS.pop(auth_code)
    log_event("ADMIN", f"DECISION_{action.upper()}", f"Amt: ${tx.amount} ({tx.client_name})", "DONE")
    return {"message": f"Transaction {auth_code} {action}ed"}

@app.get("/audit-logs", tags=["Security Console"])
async def get_logs(admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Access Denied")
    return {"history": SECURITY_LOGS}

@app.post("/system-reset", tags=["Security Console"])
async def system_reset(admin_key: str):
    if admin_key == "BLUE_PHOENIX_REBIRTH":
        SYSTEM_CONFIG["is_locked"] = False
        log_event("ADMIN", "SYSTEM_REBORN", "Lockdown cleared by Phoenix Key", "SUCCESS")
        return {"message": "System Restored. Phoenix has Risen."}
    raise HTTPException(status_code=401, detail="Wrong Key")

