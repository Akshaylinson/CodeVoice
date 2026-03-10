import httpx
import asyncio
import json
import os
from services.job_queue import JobQueue

class TTSService:
    def __init__(self):
        self.tts_engine_url = os.getenv("TTS_ENGINE_URL", "http://codvoice-tts:8000")
        self.use_workers = os.getenv("USE_WORKERS", "true").lower() == "true"
        if self.use_workers:
            self.job_queue = JobQueue()
    
    async def synthesize(self, text: str, voice: str, speaker_id: int = 0, 
                        length_scale: float = 1.0, noise_scale: float = 0.667, 
                        noise_w_scale: float = 0.8) -> bytes:
        
        if self.use_workers:
            # Use worker queue
            job_data = {
                "text": text,
                "voice": voice,
                "speaker_id": speaker_id,
                "length_scale": length_scale,
                "noise_scale": noise_scale,
                "noise_w_scale": noise_w_scale
            }
            
            job_id = await self.job_queue.enqueue_job(job_data)
            return await self.job_queue.get_result(job_id)
        else:
            # Direct HTTP call (fallback)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.tts_engine_url}/synthesize",
                    json={
                        "text": text,
                        "voice": voice,
                        "speaker_id": speaker_id,
                        "length_scale": length_scale,
                        "noise_scale": noise_scale,
                        "noise_w_scale": noise_w_scale
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
    
    async def synthesize_stream(self, text: str, voice: str, speaker_id: int = 0,
                               length_scale: float = 1.0, noise_scale: float = 0.667,
                               noise_w_scale: float = 0.8):
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.tts_engine_url}/synthesize_stream",
                json={
                    "text": text,
                    "voice": voice,
                    "speaker_id": speaker_id,
                    "length_scale": length_scale,
                    "noise_scale": noise_scale,
                    "noise_w_scale": noise_w_scale
                },
                timeout=30.0
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk