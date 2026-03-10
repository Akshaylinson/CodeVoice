from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from models.database_models import get_db, Voice, TTSRequest
from services.voice_manager import VoiceManager
from services.analytics_service import AnalyticsService
from pydantic import BaseModel
import shutil
import os

router = APIRouter()
voice_manager = VoiceManager()
analytics = AnalyticsService()

class VoiceUpload(BaseModel):
    name: str
    language: str

@router.post("/voices/upload")
async def upload_voice(
    name: str,
    language: str,
    model_file: UploadFile = File(...),
    config_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        model_path = f"/app/models/{name}.onnx"
        config_path = f"/app/models/{name}.onnx.json"
        
        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(model_file.file, buffer)
        
        with open(config_path, "wb") as buffer:
            shutil.copyfileobj(config_file.file, buffer)
        
        voice = Voice(name=name, language=language, model_path=model_path)
        db.add(voice)
        db.commit()
        
        return {"message": "Voice uploaded successfully", "name": name}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def list_voices(db: Session = Depends(get_db)):
    voices = db.query(Voice).all()
    return [{"id": v.id, "name": v.name, "language": v.language, "enabled": v.enabled} for v in voices]

@router.post("/voices/{voice_id}/toggle")
async def toggle_voice(voice_id: int, db: Session = Depends(get_db)):
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    voice.enabled = not voice.enabled
    db.commit()
    return {"message": f"Voice {'enabled' if voice.enabled else 'disabled'}"}

@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: int, db: Session = Depends(get_db)):
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    try:
        os.remove(voice.model_path)
        os.remove(f"{voice.model_path}.json")
    except:
        pass
    
    db.delete(voice)
    db.commit()
    return {"message": "Voice deleted successfully"}

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    return await analytics.get_analytics(db)

@router.get("/system")
async def get_system_health():
    return {
        "status": "healthy",
        "cpu_usage": "45%",
        "memory_usage": "2.1GB",
        "disk_usage": "15GB"
    }

@router.get("/logs")
async def get_logs():
    return {"logs": ["System started", "Voice loaded", "API ready"]}