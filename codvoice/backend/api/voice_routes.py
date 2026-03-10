from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database_models import get_db, Voice

router = APIRouter()

@router.get("/")
async def list_available_voices(db: Session = Depends(get_db)):
    voices = db.query(Voice).filter(Voice.enabled == True).all()
    return {
        voice.name: {
            "language": voice.language,
            "name": voice.name,
            "quality": "medium"
        } for voice in voices
    }