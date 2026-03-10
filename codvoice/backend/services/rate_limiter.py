import redis
import time
import os
from fastapi import HTTPException

class RateLimiter:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = redis.from_url(redis_url)
        self.default_limit = 100  # requests per minute
    
    async def check_rate_limit(self, api_key: str, limit: int = None) -> bool:
        if limit is None:
            limit = self.default_limit
        
        current_minute = int(time.time() // 60)
        key = f"rate_limit:{api_key}:{current_minute}"
        
        current_count = self.redis_client.get(key)
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        if current_count >= limit:
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Maximum {limit} requests per minute."
            )
        
        # Increment counter
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # Expire after 1 minute
        pipe.execute()
        
        return True