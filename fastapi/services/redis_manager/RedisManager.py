from typing import Dict, List, Any
# ResourceRedisManager를 import 목록에 추가합니다.

# ResourceRedisManager를 임포트한다고 가정합니다.

class RedisManager:
    """Redis 작업 관리자들의 중앙 접근점 (비동기 버전)"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
        
        



    
    
    # ✅ 추가 필요한 메서드들

    async def hset(self, key, field, value):
        """Hash SET"""
        return await self.redis.hset(key, field, value)
    
    async def hgetall(self, key):
        """Hash GET ALL"""
        return await self.redis.hgetall(key)
    
    async def hdel(self, key, *fields):
        """Hash DELETE"""
        return await self.redis.hdel(key, *fields)
    
    async def hmset(self, key, mapping):
        """Hash MSET"""
        return await self.redis.hset(key, mapping=mapping)
    
    async def zadd(self, key, mapping):
        """Sorted Set ADD"""
        return await self.redis.zadd(key, mapping)
    
    async def zrangebyscore(self, key, min_score, max_score):
        """Sorted Set RANGE BY SCORE"""
        return await self.redis.zrangebyscore(key, min_score, max_score)
    
    async def zrem(self, key, *members):
        """Sorted Set REMOVE"""
        return await self.redis.zrem(key, *members)
    
    async def keys(self, pattern):
        """KEYS with pattern"""
        return await self.redis.keys(pattern)
    
    async def get(self, key):
        """GET"""
        return await self.redis.get(key)
    
    async def setex(self, key, seconds, value):
        """SET with expiry"""
        return await self.redis.setex(key, seconds, value)
    
    async def expire(self, key, seconds):
        """SET TTL"""
        return await self.redis.expire(key, seconds)
    
    async def delete(self, *keys):
        """DELETE"""
        return await self.redis.delete(*keys)