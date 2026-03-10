from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys
import os
sys.path.append('/app')

from piper import PiperVoice, SynthesisConfig
import io
import wave
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CODVOICE TTS Engine")

# Preload voices at startup
loaded_voices = {}
models_dir = Path("/app/models")

def preload_voices():
    """Load all available voices at startup"""
    logger.info("Preloading voices...")
    
    for onnx_file in models_dir.glob("*.onnx"):
        voice_name = onnx_file.stem
        config_file = onnx_file.with_suffix(".onnx.json")
        
        if config_file.exists():
            try:
                logger.info(f"Loading voice: {voice_name}")
                voice = PiperVoice.load(str(onnx_file), use_cuda=False)
                loaded_voices[voice_name] = voice
                logger.info(f"Successfully loaded voice: {voice_name}")
            except Exception as e:
                logger.error(f"Failed to load voice {voice_name}: {e}")
    
    logger.info(f"Preloaded {len(loaded_voices)} voices: {list(loaded_voices.keys())}")

# Preload voices on startup
preload_voices()

def get_voice(voice_name: str):
    """Get preloaded voice or load on demand"""
    if voice_name in loaded_voices:
        return loaded_voices[voice_name]
    
    # Fallback: load on demand if not preloaded
    model_path = models_dir / f"{voice_name}.onnx"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Voice {voice_name} not found")
    
    logger.info(f"Loading voice on demand: {voice_name}")
    voice = PiperVoice.load(str(model_path), use_cuda=False)
    loaded_voices[voice_name] = voice
    return voice

class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "en_US-lessac-medium"
    speaker_id: int = 0
    length_scale: float = 1.0
    noise_scale: float = 0.667
    noise_w_scale: float = 0.8

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    try:
        voice = get_voice(request.voice)
        
        config = SynthesisConfig(
            speaker_id=request.speaker_id,
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w_scale=request.noise_w_scale
        )
        
        with io.BytesIO() as wav_io:
            wav_file = wave.open(wav_io, "wb")
            voice.synthesize_wav(request.text, wav_file, syn_config=config)
            wav_file.close()
            
            return StreamingResponse(
                io.BytesIO(wav_io.getvalue()),
                media_type="audio/wav"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize_stream")
async def synthesize_stream(request: SynthesizeRequest):
    try:
        voice = get_voice(request.voice)
        
        config = SynthesisConfig(
            speaker_id=request.speaker_id,
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w_scale=request.noise_w_scale
        )
        
        def generate():
            for audio_chunk in voice.synthesize(request.text, syn_config=config):
                yield audio_chunk.audio_int16_bytes
        
        return StreamingResponse(generate(), media_type="audio/wav")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def list_voices():
    voices = {}
    for onnx_file in models_dir.glob("*.onnx"):
        config_file = onnx_file.with_suffix(".onnx.json")
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
            voices[onnx_file.stem] = config
    return voices

@app.get("/health")
async def health():
    return {"status": "healthy", "loaded_voices": list(loaded_voices.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)