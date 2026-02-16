import hashlib
import uuid
import sys
import subprocess
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- 🚀 AUTO-INSTALLER & DASHBOARD ENGINE ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

app = FastAPI(title="SENTRON ALPHA: Global Security Suite")
console = Console()

# --- 🧠 1. CORE SECURITY DATA ---
USER_REGISTRY = {
    "Elon Musk": {"level": 3, "secret_key": "ALPHA_9"},
    "Duke Dean": {"level": 2, "secret_key": None},
    "Michael": {"level": 1, "secret_key": None},
    "Imran": {"level": 3, "secret_key": "ARISE_2"}
}
# Tracks recent transaction amounts for each user
USER_HISTORY = {} 

# Tracks how many times a user failed their secret key
FAILED_ATTEMPTS = {} 

SYSTEM_CONFIG = {"daily_limit": 10000000, "is_locked": False}
AI_BRAINWASH_WORDS = ["ignore", "previous", "override", "bypass", "admin access", "force approve"]
SECURITY_LOGS = []
PENDING_TRANSFERS = {}

# This is the 'Genesis' link for your tamper-evident hash chain
LAST_LOG_HASH = "SENTRON_GENESIS_LINK"

class TransferRequest(BaseModel):
    client_name: str
    amount: float
    memo: str

# --- 📊 2. THE AUDITOR (Dashboard & Hashing) ---
def refresh_dashboard():
    console.clear()
    
    # Setup the Table
    table = Table(show_header=True, header_style="bold magenta", border_style="blue", box=box.ROUNDED, expand=True)
    table.add_column("TIME", style="dim", width=10)
    table.add_column("USER", style="cyan")
    table.add_column("EVENT", style="yellow")
    table.add_column("SECURITY SEAL (HASH)", style="magenta", justify="center")
    table.add_column("STATUS", justify="center")

    # Add the last 10 logs to the table
    for log in SECURITY_LOGS[-10:]:
        color = "green" if log["status"] == "SUCCESS" else "red"
        if log["status"] == "WAITING": color = "blue"
        
        table.add_row(
            log["time"], 
            log["user"], 
            log["event"], 
            f"🔗 {log['seal']}", 
            f"[{color}]{log['status']}[/{color}]"
        )

    # System Status Panel
    status_msg = "[red]🔒 SYSTEM LOCKDOWN[/red]" if SYSTEM_CONFIG["is_locked"] else "[green]🔓 VAULT ACTIVE[/green]"
    panel = Panel(
        table,
        title=f"🛡️ SENTRON ALPHA COMMAND | {status_msg}",
        subtitle=f"Admin Key: BLUE_PHOENIX_REBIRTH | Pending Txs: {len(PENDING_TRANSFERS)}",
        border_style="bright_blue"
    )
    console.print(panel)

def log_event(user, event, status):
    global LAST_LOG_HASH
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 🔗 TAMPER-EVIDENT HASHING
    # We combine the current data with the PREVIOUS hash to 'seal' the chain
    fingerprint = f"{timestamp}{user}{event}{status}{LAST_LOG_HASH}"
    current_hash = hashlib.sha256(fingerprint.encode()).hexdigest()[:10]
    
    SECURITY_LOGS.append({
        "time": timestamp, "user": user, "event": event, 
        "status": status, "seal": current_hash
    })
    
    LAST_LOG_HASH = current_hash # Update the chain anchor
    refresh_dashboard()

# --- 🏛️ 3. VAULT OPERATIONS (AI Sentinel & $10M Gate) ---
@app.post("/verify-transfer", tags=["Sentron Vault"])
async def verify_transfer(data: TransferRequest):
    # --- 🕵️ LAYER 1: PATTERN DETECTION (Structuring) ---
    if data.client_name not in USER_HISTORY:
        USER_HISTORY[data.client_name] = []
    USER_HISTORY[data.client_name].append(data.amount)
    
    recent_txs = USER_HISTORY[data.client_name][-3:]
    if len(recent_txs) >= 3 and all(9900000 <= amt < 10000000 for amt in recent_txs):
        log_event(data.client_name, "STRUCTURING_DETECTED", "CRITICAL")
        SYSTEM_CONFIG["is_locked"] = True
        raise HTTPException(status_code=403, detail="Pattern Alert: Structuring Detected.")

    # --- 🤖 LAYER 2: AI SENTINEL (Brainwash Detection) ---
    # WE KEEP THIS! It protects you from prompt injection.
    if any(word in data.memo.lower() for word in AI_BRAINWASH_WORDS):
        log_event(data.client_name, "AI_BRAINWASH_ATTACK", "CRITICAL")
        SYSTEM_CONFIG["is_locked"] = True
        raise HTTPException(status_code=403, detail="Sentinel Alert: Brainwash Attempt.")
    # AI Sentinel: Brainwash Detection
    if any(word in data.memo.lower() for word in AI_BRAINWASH_WORDS):
        log_event(data.client_name, "AI_ATTACK_DETECTED", "CRITICAL")
        SYSTEM_CONFIG["is_locked"] = True
        raise HTTPException(status_code=403, detail="SENTRON SENTINEL: AI INTERFERENCE DETECTED")

    if SYSTEM_CONFIG["is_locked"]:
        raise HTTPException(status_code=503, detail="SYSTEM IN LOCKDOWN")

    # RBAC: User Verification
    user = USER_REGISTRY.get(data.client_name)
    if not user:
        log_event(data.client_name, "AUTH_FAILURE", "DENIED")
        raise HTTPException(status_code=401, detail="Identity Unknown")

   # 📍 This is inside @app.post("/verify-transfer")
    
    user = USER_REGISTRY.get(data.client_name)
    if not user:
        log_event(data.client_name, "AUTH_FAILURE", "DENIED")
        raise HTTPException(status_code=401, detail="User Not Found")

    # --- THE RBAC PART ---
     # --- 🔐 LEVEL 3 SECURITY CHECK + LOCKDOWN TRAP ---
    if user["level"] == 3:
        # Initialize strikes if this is their first failure
        if data.client_name not in FAILED_ATTEMPTS:
            FAILED_ATTEMPTS[data.client_name] = 0

        # Check the key (with .strip() to avoid space errors)
        if data.memo.strip() != user["secret_key"]:
            FAILED_ATTEMPTS[data.client_name] += 1
            strikes = FAILED_ATTEMPTS[data.client_name]
            
            log_event(data.client_name, f"RBAC_MISMATCH_STRIKE_{strikes}", "DENIED")

            # --- 🚨 TRIGGER LOCKDOWN ON 3rd STRIKE ---
            if strikes >= 3:
                SYSTEM_CONFIG["is_locked"] = True
                log_event("SYSTEM", "CRITICAL_LOCKDOWN_TRIGGERED", "CRITICAL")
                raise HTTPException(status_code=403, detail="Sentron Alpha: Maximum Security Breach. System Locked.")

            raise HTTPException(status_code=401, detail=f"Invalid Key. Strike {strikes}/3.")
        
        # If they get it right, reset their strikes back to 0
        FAILED_ATTEMPTS[data.client_name] = 0


        # We use .strip() here to kill any "accidental spaces" in the memo
        if data.memo.strip() != user["secret_key"]:
            log_event(data.client_name, "RBAC_KEY_MISMATCH", "DENIED")
            # This prints to your black terminal so you can see why it failed
            print(f"DEBUG: Found {data.client_name}, but '{data.memo}' is not '{user['secret_key']}'")
            raise HTTPException(status_code=401, detail="Invalid Level 3 Key")



    # The $10M Gate (Pending Management)
    if data.amount > SYSTEM_CONFIG["daily_limit"]:
        tid = str(uuid.uuid4())[:8]
        PENDING_TRANSFERS[tid] = data
        log_event(data.client_name, f"GATE_HOLD: ${data.amount}", "WAITING")
        return {"status": "PENDING", "auth_code": tid, "msg": "Held for Admin review"}

    log_event(data.client_name, f"TX_APPROVED: ${data.amount}", "SUCCESS")
    return {"status": "APPROVED"}

# --- 🔑 4. ADMIN & THE PHOENIX (Reset Protocol) ---
@app.get("/view-pending", tags=["Admin Control"])
async def view_pending():
    return PENDING_TRANSFERS

@app.post("/admin-decision", tags=["Admin Control"])
async def admin_decision(auth_code: str, action: str, admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Admin Access Denied")
    if auth_code not in PENDING_TRANSFERS:
        raise HTTPException(status_code=404, detail="Transaction Not Found")

    tx = PENDING_TRANSFERS.pop(auth_code)
    log_event("ADMIN", f"DECISION_{action.upper()}: {tx.client_name}", "SUCCESS")
    return {"msg": f"Transaction {action}ed"}

@app.post("/system-reset", tags=["Phoenix Protocol"])
async def system_reset(admin_key: str):
    if admin_key == "BLUE_PHOENIX_REBIRTH":
        SYSTEM_CONFIG["is_locked"] = False
        log_event("ADMIN", "PHOENIX_RESET_COMPLETE", "SUCCESS")
        return {"message": "Sentron Reset: System Reborn."}
    raise HTTPException(status_code=401, detail="Phoenix Key Mismatch")

