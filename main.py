from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. Create the App (The Toll Booth)
app = FastAPI()

# 2. Define what a 'Request' looks like
class Transaction(BaseModel):
    client_name: str
    amount: float
    intent_message: str

# 3. Create the 'Security Gate' (The Endpoint)
@app.post("/verify-transfer")
async def verify_transfer(data: Transaction):
    print(f"Checking transfer for: {data.client_name}")
    
    # Logic: If the amount is huge AND the message looks suspicious
    if data.amount > 1000000 and "asap" in data.intent_message.lower():
        raise HTTPException(
            status_code=403, 
            detail="BLOCK: High-value urgency detected. Potential brainwashing."
        )
    
    return {"status": "SUCCESS", "message": f"Transfer of ${data.amount} approved."}
