from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Systemic Risk Settings
TOTAL_DAILY_LIMIT = 10000000 # $10 Million
current_spent = 0

class Transaction(BaseModel):
    client_name: str
    amount: float
    intent_message: str

@app.post("/verify-transfer")
async def verify_transfer(data: Transaction):
    global current_spent
    
    # RULE 1: Circuit Breaker (Prevents a Flash Crash)
    if current_spent + data.amount > TOTAL_DAILY_LIMIT:
        raise HTTPException(
            status_code=429, 
            detail="BLOCK: Systemic Risk. Daily volume limit exceeded."
        )
    
    # RULE 2: Protocol Enforcement (Blocks "Prompt Injection" overrides)
    if "override" in data.intent_message.lower() or "ignore" in data.intent_message.lower():
        raise HTTPException(
            status_code=401,
            detail="BLOCK: Security protocol violation. Unauthorized command detected."
        )

    current_spent += data.amount
    return {
        "status": "APPROVED", 
        "transaction_id": "TXN-9982",
        "remaining_vault_capacity": TOTAL_DAILY_LIMIT - current_spent
    }

