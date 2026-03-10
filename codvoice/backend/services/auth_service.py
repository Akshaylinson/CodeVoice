from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from models.database_models import get_db, APIKey

async def get_api_key(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="API key required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    
    key_record = db.query(APIKey).filter(APIKey.api_key == api_key).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return key_record