import sys
import os
sys.path.append('/app')

from piper import PiperVoice, SynthesisConfig
import io
import wave
import json
import logging
from pathlib import Path
from services.job_queue import JobQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSWorker:
    def __init__(self):
        self.job_queue = JobQueue()
        self.loaded_voices = {}
        self.models_dir = Path("/app/models")
        self.preload_voices()
    
    def preload_voices(self):
        """Load all available voices at startup"""
        logger.info("Worker: Preloading voices...")
        
        for onnx_file in self.models_dir.glob("*.onnx"):
            voice_name = onnx_file.stem
            config_file = onnx_file.with_suffix(".onnx.json")
            
            if config_file.exists():
                try:
                    logger.info(f"Worker: Loading voice: {voice_name}")
                    voice = PiperVoice.load(str(onnx_file), use_cuda=False)
                    self.loaded_voices[voice_name] = voice
                    logger.info(f"Worker: Successfully loaded voice: {voice_name}")
                except Exception as e:
                    logger.error(f"Worker: Failed to load voice {voice_name}: {e}")
        
        logger.info(f"Worker: Preloaded {len(self.loaded_voices)} voices")
    
    def get_voice(self, voice_name: str):
        """Get preloaded voice"""
        if voice_name not in self.loaded_voices:
            raise ValueError(f"Voice {voice_name} not available")
        return self.loaded_voices[voice_name]
    
    def synthesize_audio(self, job_data):
        """Process TTS synthesis job"""
        try:
            voice = self.get_voice(job_data["voice"])
            
            config = SynthesisConfig(
                speaker_id=job_data.get("speaker_id", 0),
                length_scale=job_data.get("length_scale", 1.0),
                noise_scale=job_data.get("noise_scale", 0.667),
                noise_w_scale=job_data.get("noise_w_scale", 0.8)
            )
            
            with io.BytesIO() as wav_io:
                wav_file = wave.open(wav_io, "wb")
                voice.synthesize_wav(job_data["text"], wav_file, syn_config=config)
                wav_file.close()
                return wav_io.getvalue()
        
        except Exception as e:
            logger.error(f"Worker: Synthesis failed: {e}")
            raise
    
    def run(self):
        """Main worker loop"""
        logger.info("Worker: Starting TTS worker...")
        
        while True:
            try:
                job = self.job_queue.dequeue_job()
                if job:
                    logger.info(f"Worker: Processing job {job['job_id']}")
                    
                    audio_data = self.synthesize_audio(job)
                    self.job_queue.store_result(job["job_id"], audio_data)
                    
                    logger.info(f"Worker: Completed job {job['job_id']}")
            
            except Exception as e:
                logger.error(f"Worker: Error processing job: {e}")

if __name__ == "__main__":
    worker = TTSWorker()
    worker.run()