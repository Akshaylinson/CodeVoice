from sqlalchemy.orm import Session
from models.database_models import TTSRequest
from sqlalchemy import func
import redis
import os

class AnalyticsService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = redis.from_url(redis_url)
    
    async def log_request(self, voice: str, latency: int, text_length: int, 
                         audio_length: int, status: str):
        # Store in Redis for real-time metrics
        self.redis_client.incr(f"requests:{voice}")
        self.redis_client.incr(f"requests:total")
        
        # Will be stored in database via background task
        request_data = {
            "voice": voice,
            "latency": latency,
            "text_length": text_length,
            "audio_length": audio_length,
            "status": status
        }
        return request_data
    
    async def get_analytics(self, db: Session):
        # Get request counts by voice
        voice_stats = db.query(
            TTSRequest.voice,
            func.count(TTSRequest.id).label('count'),
            func.avg(TTSRequest.latency).label('avg_latency')
        ).group_by(TTSRequest.voice).all()
        
        # Get total requests
        total_requests = db.query(func.count(TTSRequest.id)).scalar()
        
        # Get recent requests
        recent_requests = db.query(TTSRequest).order_by(
            TTSRequest.timestamp.desc()
        ).limit(10).all()
        
        return {
            "total_requests": total_requests,
            "voice_stats": [
                {
                    "voice": stat.voice,
                    "count": stat.count,
                    "avg_latency": round(stat.avg_latency, 2) if stat.avg_latency else 0
                }
                for stat in voice_stats
            ],
            "recent_requests": [
                {
                    "voice": req.voice,
                    "latency": req.latency,
                    "status": req.status,
                    "timestamp": req.timestamp.isoformat()
                }
                for req in recent_requests
            ]
        }