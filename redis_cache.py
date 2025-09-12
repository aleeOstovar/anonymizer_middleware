"""
Redis caching strategy for the PII anonymizer module.
Implements the Strategy pattern for Redis-based caching.
"""

import json
from typing import Optional, Any
import redis
from interfaces import ICacheStrategy


class RedisCache(ICacheStrategy):
    """Redis cache implementation for distributed caching"""
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6379, 
        db: int = 0, 
        password: Optional[str] = None,
        key_prefix: str = "pii_anonymizer:",
        expiration_time: int = 3600  # 1 hour default
    ):
        """
        Initialize Redis cache
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            key_prefix: Prefix for all keys stored in Redis
            expiration_time: Time in seconds before keys expire (0 for no expiration)
        """
        self._redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False  
        )
        self._key_prefix = key_prefix
        self._expiration_time = expiration_time
    
    def _format_key(self, key: str) -> str:
        """Format key with prefix"""
        return f"{self._key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        formatted_key = self._format_key(key)
        value = self._redis.get(formatted_key)
        
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in Redis cache with expiration"""
        formatted_key = self._format_key(key)
        
        try:
            serialized_value = json.dumps(value)
            if self._expiration_time > 0:
                self._redis.setex(
                    formatted_key, 
                    self._expiration_time, 
                    serialized_value
                )
            else:
                self._redis.set(formatted_key, serialized_value)
        except (TypeError, ValueError):
            pass
    
    def clear(self) -> None:
        """Clear all keys with this prefix"""
        pattern = f"{self._key_prefix}*"
        cursor = 0
        while True:
            cursor, keys = self._redis.scan(cursor, pattern, 100)
            if keys:
                self._redis.delete(*keys)
            if cursor == 0:
                break