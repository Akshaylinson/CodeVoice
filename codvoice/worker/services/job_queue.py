import redis
import json
import uuid
import asyncio
import os
from typing import Dict, Any

class JobQueue:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = redis.from_url(redis_url)
        self.job_queue = "tts_jobs"
        self.result_prefix = "tts_result:"
        
    async def enqueue_job(self, job_data: Dict[str, Any]) -> str:
        """Add a TTS job to the queue"""
        job_id = str(uuid.uuid4())
        job_data["job_id"] = job_id
        
        self.redis_client.lpush(self.job_queue, json.dumps(job_data))
        return job_id
    
    async def get_result(self, job_id: str, timeout: int = 30) -> bytes:
        """Wait for job result"""
        result_key = f"{self.result_prefix}{job_id}"
        
        for _ in range(timeout * 10):  # Check every 100ms
            result = self.redis_client.get(result_key)
            if result:
                self.redis_client.delete(result_key)  # Clean up
                return result
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Job {job_id} timed out")
    
    def dequeue_job(self) -> Dict[str, Any]:
        """Get next job from queue (blocking)"""
        result = self.redis_client.brpop(self.job_queue, timeout=1)
        if result:
            return json.loads(result[1])
        return None
    
    def store_result(self, job_id: str, result: bytes):
        """Store job result"""
        result_key = f"{self.result_prefix}{job_id}"
        self.redis_client.setex(result_key, 300, result)  # Expire in 5 minutes