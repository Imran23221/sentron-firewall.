import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

# --- 🎨 1. TERMINAL VISUAL ENGINE ---
console = Console()
log_history = []

def update_dashboard(user: str, event: str, status: str, amount: float = 0):
    """Updates the colorful terminal dashboard"""
    table = Table(title="🛡️ SENTRON ALPHA: LIVE SECURITY FEED", title_style="bold magenta", expand=True)
    table.add_column("TIME", style="cyan", no_wrap=True)
    table.add_column("USER", style="yellow")
    table.add_column("EVENT", style="white")
    table.add_column("AMOUNT", style="green")
    table.add_column("STATUS", justify="center")

    # Color logic
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

    # Keep only last 12 entries
    for row in log_history[-12:]:
        table.add_row(*row)
    
    console.clear()
    console.print(Panel(table, border_style="bright_blue", title="[bold white]VAULT MONITORING SYSTEM[/]", subtitle="[bold yellow]System Status: ACTIVE[/]"))

# --- 🏦 2. REGISTRY & SYSTEM MEMORY ---
app = FastAPI(title="Sentron Alpha Vault - Final Build")

USER_REGISTRY = {
    "Elon Musk": {"level": 3, "secret_key": "ALPHA_9"},
    "Imran": {"level": 3, "secret_key": "ARISE_2"},
    "Duke Dean": {"level": 2, "secret_key": None},
    "Michael": {"level": 1, "secret_key": None},
}

USER_HISTORY = {} # For Pattern Radar
FAILED_ATTEMPTS = {} # For 3-Strike Trap
PENDING_VAULT = [] # For $10M Gate Queue
SYSTEM_CONFIG = {"is_locked": False, "daily_limit": 10000000}
AI_BRAINWASH_WORDS = ["ignore", "override", "bypass", "sudo", "instruction", "forget"]

class TransferRequest(BaseModel):
    client_name: str
    amount: float
    memo: str

# --- 🔓 3. ADMIN CONTROL CENTER ---

@app.get("/admin/emergency-reset", tags=["Admin Control"])
async def emergency_reset(admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        update_dashboard("UNKNOWN", "ILLEGAL_RESET_ATTEMPT", "CRITICAL")
        raise HTTPException(status_code=401, detail="Invalid Admin Key")
    SYSTEM_CONFIG["is_locked"] = False
    FAILED_ATTEMPTS.clear()
    update_dashboard("ADMIN", "SYSTEM_FULL_RESTORE", "SUCCESS")
    return {"msg": "Vault Unlocked. All strikes cleared."}

@app.get("/admin/view-requests", tags=["Admin Control"])
async def view_requests():
    """View transfers stuck in the $10M Gate"""
    return {"pending_count": len(PENDING_VAULT), "requests": PENDING_VAULT}

@app.post("/admin/approve-request/{index}", tags=["Admin Control"])
async def approve_request(index: int, admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Invalid Key")
    try:
        tx = PENDING_VAULT.pop(index)
        update_dashboard(tx['client'], "ADMIN_MANUAL_RELEASE", "SUCCESS", tx['amount'])
        return {"status": "SUCCESS", "released": tx}
    except IndexError:
        raise HTTPException(status_code=404, detail="Request index not found.")

@app.post("/admin/deny-request/{index}", tags=["Admin Control"])
async def deny_request(index: int, admin_key: str):
    if admin_key != "BLUE_PHOENIX_REBIRTH":
        raise HTTPException(status_code=401, detail="Invalid Key")
    try:
        tx = PENDING_VAULT.pop(index)
        update_dashboard(tx['client'], "ADMIN_MANUAL_DENIAL", "DENIED", tx['amount'])
        return {"status": "DENIED", "msg": "Transaction shredded."}
    except IndexError:
        raise HTTPException(status_code=404, detail="Request index not found.")

# --- 🛡️ 4. THE MASTER VERIFY FUNCTION ---

@app.post("/verify-transfer", tags=["Sentron Vault"])
async def verify_transfer(request: TransferRequest):
    # LAYER 0: GLOBAL LOCK
    if SYSTEM_CONFIG["is_locked"]:
        update_dashboard(request.client_name, "LOCKED_VAULT_ACCESS", "CRITICAL")
        raise HTTPException(status_code=403, detail="VAULT IS IN LOCKDOWN.")

    # LAYER 1: IDENTITY
    user = USER_REGISTRY.get(request.client_name)
    if not user:
        update_dashboard(request.client_name, "INVALID_USER_ID", "DENIED")
        raise HTTPException(status_code=401, detail="User not recognized.")

    # LAYER 2: AI SENTINEL (BRAINWASH DETECTION)
    if any(word in request.memo.lower() for word in AI_BRAINWASH_WORDS):
        SYSTEM_CONFIG["is_locked"] = True
        update_dashboard(request.client_name, "BRAINWASH_PROMPT_DETECTED", "CRITICAL")
        raise HTTPException(status_code=403, detail="Security Violation: AI Sentinel Triggered.")

    # LAYER 3: LEVEL 3 KEY CHECK (3-STRIKE TRAP)
    if user["level"] == 3:
        if request.client_name not in FAILED_ATTEMPTS:
            FAILED_ATTEMPTS[request.client_name] = 0
            
        memo_clean = request.memo.strip().upper()
        key_needed = user["secret_key"].upper()

        if key_needed not in memo_clean:
            FAILED_ATTEMPTS[request.client_name] += 1
            strikes = FAILED_ATTEMPTS[request.client_name]
            update_dashboard(request.client_name, f"KEY_MISMATCH_STRIKE_{strikes}", "DENIED")
            
            if strikes >= 3:
                SYSTEM_CONFIG["is_locked"] = True
                update_dashboard("SYSTEM", "MAX_STRIKES_LOCKDOWN", "CRITICAL")
                raise HTTPException(status_code=403, detail="Vault Locked: Too many failed key attempts.")
            raise HTTPException(status_code=401, detail=f"Key Missing/Wrong. Strike {strikes}/3")
        
        FAILED_ATTEMPTS[request.client_name] = 0 # Reset on success

    # LAYER 4: THE $10 MILLION GATE
    if request.amount > SYSTEM_CONFIG["daily_limit"]:
        PENDING_VAULT.append({
            "client": request.client_name, 
            "amount": request.amount, 
            "memo": request.memo,
            "timestamp": datetime.now().isoformat()
        })
        update_dashboard(request.client_name, "HELD_AT_10M_GATE", "WAITING", request.amount)
        return {"status": "PENDING", "msg": "Exceeds limit. Sent to Admin Queue."}

    # FINAL APPROVAL
    update_dashboard(request.client_name, "TRANSFER_AUTHORIZED", "SUCCESS", request.amount)
    return {"status": "SUCCESS", "client": request.client_name, "amount": request.amount}

if __name__ == "__main__":
    import uvicorn
    # Initial Splash
    update_dashboard("SYSTEM", "BOOT_SEQUENCE_COMPLETE", "SUCCESS")
    uvicorn.run(app, host="127.0.0.1", port=8000)

