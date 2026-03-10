from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.tts_service import TTSService
from services.analytics_service import AnalyticsService
import time
import io

router = APIRouter()
tts_service = TTSService()
analytics = AnalyticsService()

class TTSRequest(BaseModel):
    text: str
    voice: str = "en_US-lessac-medium"
    speaker_id: int = 0
    length_scale: float = 1.0
    noise_scale: float = 0.667
    noise_w_scale: float = 0.8

@router.post("/")
async def synthesize_tts(request: TTSRequest):
    start_time = time.time()
    
    try:
        audio_data = await tts_service.synthesize(
            text=request.text,
            voice=request.voice,
            speaker_id=request.speaker_id,
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w_scale=request.noise_w_scale
        )
        
        latency = int((time.time() - start_time) * 1000)
        
        await analytics.log_request(
            voice=request.voice,
            latency=latency,
            text_length=len(request.text),
            audio_length=len(audio_data),
            status="success"
        )
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except Exception as e:
        await analytics.log_request(
            voice=request.voice,
            latency=int((time.time() - start_time) * 1000),
            text_length=len(request.text),
            audio_length=0,
            status="error"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def synthesize_stream(request: TTSRequest):
    try:
        async def generate():
            async for chunk in tts_service.synthesize_stream(
                text=request.text,
                voice=request.voice,
                speaker_id=request.speaker_id,
                length_scale=request.length_scale,
                noise_scale=request.noise_scale,
                noise_w_scale=request.noise_w_scale
            ):
                yield chunk
        
        return StreamingResponse(generate(), media_type="audio/wav")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))