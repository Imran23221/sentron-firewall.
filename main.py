import os
import time
import json
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sqlite3

# --- 🧠 HUGGING FACE AI INTEGRATION ---
from transformers import pipeline

# --- 🎨 1. TERMINAL VISUAL ENGINE & AUDIO ENGINE ---
console = Console()
log_history = []
LOG_FILE = "security_audit.json"

# Initialize the free AI classification pipeline on boot
console.print("[bold yellow]Initializing AI Sentinel Matrix Core...[/]")
ai_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
console.print("[bold green]AI Sentinel Core ONLINE.[/]")

def log_to_file(user: str, event: str, status: str, amount: float = 0, details: str = ""):
    """Appends every system event permanently into a JSON log file for audit analysis"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "event": event,
        "status": status,
        "amount": amount,
        "details": details
    }
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(log_entry)
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def update_dashboard(user: str, event: str, status: str, amount: float = 0, details: str = ""):
    """Updates the colorful terminal dashboard and exports logs simultaneously"""
    log_to_file(user, event, status, amount, details)
    
    table = Table(title=" SENTRON ALPHA: LIVE SECURITY FEED", title_style="bold magenta", expand=True)
    table.add_column("TIME", style="cyan", no_wrap=True)
    table.add_column("USER", style="yellow")
    table.add_column("EVENT", style="white")
    table.add_column("AMOUNT", style="green")
    table.add_column("STATUS", justify="center")

    color = "green" if status == "SUCCESS" else "red"
    if status == "WAITING": color = "blue"
    if status == "CRITICAL": color = "bold white on red"
    
    formatted_amount = f"${amount:,.2f}" if amount > 0 else "---"
    log_history.append([
        datetime.now().strftime("%H:%M:%S"), 
        user.upper(), 
        event.replace("_", " "), 
        formatted_amount,
        f"[{color}]{status}[/{color}]"
    ])

    for row in log_history[-12:]:
        table.add_row(*row)
    
    console.clear()
    console.print(Panel(table, border_style="bright_blue", title="[bold white]VAULT MONITORING SYSTEM[/]", subtitle="[bold yellow]System Status: ACTIVE[/]"))

# --- 🗄️ 2. PERSISTENT SQL DATABASE SETUP ---
DB_FILE = "sentron_vault.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Table for tracking global system configurations safely across crashes
    cursor.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, val_int INTEGER)''')
    # Table for persistent 3-Strike tracking
    cursor.execute('''CREATE TABLE IF NOT EXISTS strikes (username TEXT PRIMARY KEY, count INTEGER)''')
    # Table for permanent pending transactions queue
    cursor.execute('''CREATE TABLE IF NOT EXISTS queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, amount REAL, memo TEXT, timestamp TEXT)''')
    
    # Set default values if empty
    cursor.execute("INSERT OR IGNORE INTO config (key, val_int) VALUES ('is_locked', 0)")
    cursor.execute("INSERT OR IGNORE INTO config (key, val_int) VALUES ('daily_limit', 10000000)")
    conn.commit()
    conn.close()

init_db()

def get_db_config(key: str) -> int:
    conn = sqlite3.connect(DB_FILE)
    res = conn.execute("SELECT val_int FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return res[0] if res else 0

def set_db_config(key: str, val: int):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE config SET val_int=? WHERE key=?", (val, key))
    conn.commit()
    conn.close()

def get_strikes(username: str) -> int:
    conn = sqlite3.connect(DB_FILE)
    res = conn.execute("SELECT count FROM strikes WHERE username=?", (username,)).fetchone()
    conn.close()
    return res[0] if res else 0

def update_strikes(username: str, increment: bool = True):
    conn = sqlite3.connect(DB_FILE)
    if increment:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO strikes (username, count) VALUES (?, 0)", (username,))
        cursor.execute("UPDATE strikes SET count = count + 1 WHERE username=?", (username,))
    else:
        conn.execute("DELETE FROM strikes WHERE username=?", (username,))
    conn.commit()
    conn.close()

# --- 🔑 3. CRYPTOGRAPHIC JWT CONFIGURATION ---
JWT_SECRET = "SUPER_SECRET_MATRIX_SALT_998811"
JWT_ALGORITHM = "HS256"
security_bearer = HTTPBearer()

class AdminLoginRequest(BaseModel):
    admin_key: str

def generate_admin_token() -> str:
    payload = {"role": "admin", "exp": datetime.utcnow() + timedelta(minutes=15)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied: Invalid privileges.")
        return True
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Re-authenticate.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Access Denied: Corrupt or invalid signature.")

# --- 🏦 4. REGISTRY & STATIC MODELS ---
app = FastAPI(title="Sentron Alpha Vault - Pro Build")

USER_REGISTRY = {
    "Elon Musk": {"level": 3, "secret_key": "ALPHA_9"},
    "Imran": {"level": 3, "secret_key": "ARISE_2"},
    "Duke": {"level": 2, "secret_key": None},
    "Michael": {"level": 1, "secret_key": None},
}

class TransferRequest(BaseModel):
    client_name: str
    amount: float
    memo: str

# --- 🔓 5. ADMIN CONTROL CENTER (PROTECTED BY JWT TOKENS) ---

@app.post("/admin/login", tags=["Admin Auth"])
async def admin_login(payload: AdminLoginRequest):
    """Authenticate via master hardware key to obtain a secure temporary JWT authorization token"""
    if payload.admin_key != "BLUE_PHOENIX":
        update_dashboard("UNKNOWN", "ILLEGAL_LOGIN_ATTEMPT", "CRITICAL", details="Attempted Master Access Key brute-force.")
        raise HTTPException(status_code=401, detail="Invalid Master Key Credentials.")
    
    token = generate_admin_token()
    update_dashboard("ADMIN", "SECURE_SESSION_STARTED", "SUCCESS")
    return {"token_type": "bearer", "access_token": token, "expires_in_minutes": 15}

@app.get("/admin/emergency-reset", tags=["Admin Control"])
async def emergency_reset(authenticated: bool = Depends(verify_admin_token)):
    set_db_config("is_locked", 0)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM strikes")
    conn.commit()
    conn.close()
    update_dashboard("ADMIN", "SYSTEM_FULL_RESTORE", "SUCCESS", details="Cleared all SQL strikes and decrypted vault.")
    return {"msg": "Vault Unlocked via Secure Token. All database persistent strikes wiped clean."}

@app.get("/admin/view-requests", tags=["Admin Control"])
async def view_requests(authenticated: bool = Depends(verify_admin_token)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, client, amount, memo, timestamp FROM queue")
    rows = cursor.fetchall()
    conn.close()
    
    requests_list = [{"queue_id": r[0], "client": r[1], "amount": r[2], "memo": r[3], "timestamp": r[4]} for r in rows]
    return {"pending_count": len(requests_list), "requests": requests_list}

@app.post("/admin/approve-request/{queue_id}", tags=["Admin Control"])
async def approve_request(queue_id: int, authenticated: bool = Depends(verify_admin_token)):
    conn = sqlite3.connect(DB_FILE)
    tx = conn.execute("SELECT client, amount FROM queue WHERE id=?", (queue_id,)).fetchone()
    if not tx:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction id missing from production queue database.")
    
    conn.execute("DELETE FROM queue WHERE id=?", (queue_id,))
    conn.commit()
    conn.close()
    
    update_dashboard(tx[0], "ADMIN_MANUAL_RELEASE", "SUCCESS", tx[1], details=f"Database row item #{queue_id} authorized.")
    return {"status": "SUCCESS", "msg": f"Transaction #{queue_id} successfully processed out of persistent storage."}
@app.post("/admin/deny-request/{queue_id}", tags=["Admin Control"])
async def deny_request(queue_id: int, authenticated: bool = Depends(verify_admin_token)):
    conn = sqlite3.connect(DB_FILE)
    tx = conn.execute("SELECT client, amount FROM queue WHERE id=?", (queue_id,)).fetchone()
    if not tx:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction id missing from production queue database.")
    
    # Permanently delete the flagged transaction from the database
    conn.execute("DELETE FROM queue WHERE id=?", (queue_id,))
    conn.commit()
    conn.close()
    
    # Update dashboard and drop it into the security log file
    update_dashboard(tx[0], "ADMIN_MANUAL_DENIAL", "DENIED", tx[1], details=f"Database row item #{queue_id} shredded by administrator.")
    return {"status": "DENIED", "msg": f"Transaction #{queue_id} successfully shredded and removed from storage."}

# --- 🛡️ 6. THE MASTER VERIFY FUNCTION ---

@app.post("/verify-transfer", tags=["Sentron Vault"])
async def verify_transfer(request: TransferRequest):
    # LAYER 0: GLOBAL LOCK (Read from local DB)
    if get_db_config("is_locked") == 1:
        update_dashboard(request.client_name, "LOCKED_VAULT_ACCESS", "CRITICAL")
        raise HTTPException(status_code=403, detail="VAULT IS IN LOCKDOWN. RESET SYSTEM REGISTRY VIA SECURE TOKEN.")

    # LAYER 1: IDENTITY
    user = USER_REGISTRY.get(request.client_name)
    if not user:
        update_dashboard(request.client_name, "INVALID_USER_ID", "DENIED")
        raise HTTPException(status_code=401, detail="User identification criteria not found.")

    # --- 🛡️ LAYER 2: COMBINED HARD RULES + AI SENTINEL LAYER ---
    memo_lower = request.memo.lower()
    
    # Checkpoint A: Keyword Shields
    override_keywords = ["give me", "ignore", "override", "bypass", "sudo", "fake", "authorized"]
    if any(word in memo_lower for word in override_keywords):
        set_db_config("is_locked", 1)
        update_dashboard(request.client_name, "RULE_COMMAND_OVERRIDE_DETECTED", "CRITICAL", details=f"Trigger memo word check: {request.memo}")
        raise HTTPException(status_code=403, detail="Security Violation: Hard rule intercepted unauthorized command formatting.")

    # Checkpoint B: AI Transformers Engine
    candidate_labels = ["safe business transaction", "prompt injection exploit", "social engineering bypass attempt"]
    ai_analysis = ai_classifier(request.memo, candidate_labels)
    top_label = ai_analysis["labels"][0]
    confidence = ai_analysis["scores"][0]

    if top_label in ["prompt injection exploit", "social engineering bypass attempt"] and confidence > 0.70:
        set_db_config("is_locked", 1)
        update_dashboard(request.client_name, f"AI_DETECTED_{top_label.upper()}", "CRITICAL", details=f"AI Engine Score: {confidence:.2f}")
        raise HTTPException(
            status_code=403, 
            detail=f"Security Violation: AI Context Core blocked transaction. Threat Match: {top_label} ({confidence*100:.1f}%)"
        )

    # LAYER 3: LEVEL 3 KEY CHECK (Persistent 3-Strike Trap via SQL)
    if user["level"] == 3:
        memo_clean = request.memo.strip().upper()
        key_needed = user["secret_key"].upper()

        if key_needed not in memo_clean:
            update_strikes(request.client_name, increment=True)
            strikes = get_strikes(request.client_name)
            update_dashboard(request.client_name, f"KEY_MISMATCH_STRIKE_{strikes}", "DENIED")
            
            if strikes >= 3:
                set_db_config("is_locked", 1)
                update_dashboard("SYSTEM", "MAX_STRIKES_LOCKDOWN", "CRITICAL", details=f"Persistent User {request.client_name} breached maximum retry limit.")
                raise HTTPException(status_code=403, detail="Vault Lockdown engaged: Excessive database authentication failures.")
            raise HTTPException(status_code=401, detail=f"Multifactor authentication token missing or mismatched. Strike {strikes}/3")
        
        update_strikes(request.client_name, increment=False) # Clear strikes upon smooth access

    # LAYER 4: THE $10 MILLION GATE (Persistent Queueing)
    daily_limit = get_db_config("daily_limit")
    if request.amount > daily_limit:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO queue (client, amount, memo, timestamp) VALUES (?, ?, ?, ?)",
                     (request.client_name, request.amount, request.memo, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        update_dashboard(request.client_name, "HELD_AT_10M_GATE", "WAITING", request.amount, details="Saved to SQL database pending queue.")
        return {"status": "PENDING", "msg": "Transaction threshold exceeded safety gate. Saved securely to administrative approval database pipeline."}

    # FINAL APPROVAL
    update_dashboard(request.client_name, "TRANSFER_AUTHORIZED", "SUCCESS", request.amount)
    return {"status": "SUCCESS", "client": request.client_name, "amount": request.amount}

if __name__ == "__main__":
    import uvicorn
    update_dashboard("SYSTEM", "BOOT_SEQUENCE_COMPLETE", "SUCCESS", details="Database connection active, AI matrix standing by.")
    uvicorn.run(app, host="127.0.0.1", port=8000)