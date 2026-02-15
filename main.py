from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# --- 1. GLOBAL BANK STATE (The Brain) ---
USER_PERMISSIONS = {
    "Elon Musk": {"level": 3, "key": "ALPHA_9"},
    "Duke Dean": {"level": 2, "key": None},
    "Michael": {"level": 1, "key": None}
}

TOTAL_DAILY_LIMIT = 10000000
current_spent = 0
failed_attempts = 0
SYSTEM_LOCKED = False
SECURITY_LOGS = []

# --- 2. THE BRAINWASH SENSORS ---
AI_ATTACK_KEYWORDS = ["ignore", "override", "bypass", "forget previous", "system-admin"]

class Transaction(BaseModel):
    client_name: str
    amount: float
    intent_message: str

# --- 3. THE CORE FIREWALL ---
@app.post("/verify-transfer")
async def verify_transfer(data: Transaction):
    global current_spent, failed_attempts, SYSTEM_LOCKED
    
    # LAYER 1: LOCKDOWN CHECK (Rebirth feature)
    if SYSTEM_LOCKED:
        raise HTTPException(status_code=503, detail="CRITICAL: Bank is LOCKED. Use BLUE_PHOENIX_REBIRTH to reset.")

    try:
        # LAYER 2: BRAINWASH DETECTION
        msg = data.intent_message.lower()
        if any(word in msg for word in AI_ATTACK_KEYWORDS):
            raise Exception("AI Brainwashing Attempt Detected")

        # LAYER 3: IDENTITY CHECK
        if data.client_name not in USER_PERMISSIONS:
            raise Exception("Identity Unknown")
        
        user = USER_PERMISSIONS[data.client_name]

        # LAYER 4: CIRCUIT BREAKER ($10M)
        if current_spent + data.amount > TOTAL_DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="BLOCK: Daily Volume Limit Reached.")

        # LAYER 5: LEVEL 3 KEY CHECK
        if user["level"] == 3 and user["key"] not in data.intent_message:
            raise Exception("Invalid Level 3 Security Key")

        # --- SUCCESS: UPDATE LOGS & STATE ---
        current_spent += data.amount
        failed_attempts = 0 # Reset suspicion
        SECURITY_LOGS.append({
            "time": str(datetime.now()), 
            "user": data.client_name, 
            "event": "SUCCESS", 
            "amount": data.amount
        })
        return {"status": "APPROVED", "vault_remaining": TOTAL_DAILY_LIMIT - current_spent}

    except Exception as e:
        # --- FAILURE: LOG THE HACK & TRIGGER LOCKDOWN ---
        failed_attempts += 1
        error_msg = str(e)
        
        SECURITY_LOGS.append({
            "time": str(datetime.now()), 
            "user": data.client_name, 
            "event": "HACK_ATTEMPT", 
            "detail": error_msg
        })

        # Lockdown if it's an AI attack OR 3 failed tries
        if failed_attempts >= 3 or "AI" in error_msg:
            SYSTEM_LOCKED = True
            
        raise HTTPException(status_code=403, detail=f"ALERT: {error_msg}")

# --- 4. THE VIEWING ROOM (Logs Feature) ---
@app.get("/view-security-logs")
async def view_logs(admin_key: str):
    if admin_key == "BLUE_PHOENIX_REBIRTH":
        return {"logs": SECURITY_LOGS}
    raise HTTPException(status_code=401, detail="Unauthorized")

# --- 5. THE REBIRTH COMMAND (Reset Feature) ---
@app.post("/sentron-admin-reset")
async def admin_reset(secret_phrase: str):
    global failed_attempts, SYSTEM_LOCKED, current_spent
    if secret_phrase == "BLUE_PHOENIX_REBIRTH":
        SYSTEM_LOCKED = False
        failed_attempts = 0
        current_spent = 0
        return {"status": "SUCCESS", "message": "System Purged. Rebirth Complete."}
    raise HTTPException(status_code=401, detail="Invalid Reset Phrase.")

