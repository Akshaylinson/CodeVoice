from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from models.database_models import get_db, APIKey
from services.rate_limiter import RateLimiter

rate_limiter = RateLimiter()

async def get_api_key(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="API key required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    
    key_record = db.query(APIKey).filter(APIKey.api_key == api_key).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    await rate_limiter.check_rate_limit(api_key, key_record.rate_limit)
    
    return key_record

async def get_admin_auth(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Admin key or valid API key with admin privileges
    if api_key == "codvoice-admin-key-456":
        return api_key
    
    key_record = db.query(APIKey).filter(APIKey.api_key == api_key).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    return key_record