"""
Redis caching strategy for the PII anonymizer module.
Implements the Strategy pattern for Redis-based caching.
"""

import json
import os
from typing import Optional, Any
import redis
from interfaces import ICacheStrategy


class RedisCache(ICacheStrategy):
    """Redis cache implementation for distributed caching"""
    
    def __init__(
        self, 
        host: str = None, 
        port: int = None, 
        db: int = None, 
        password: Optional[str] = None,
        key_prefix: str = None,
        expiration_time: int = None
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
        # Get configuration from environment variables with fallbacks
        self._redis = redis.Redis(
            host=host or os.environ.get('REDIS_HOST', 'localhost'),
            port=int(port or os.environ.get('REDIS_PORT', 6379)),
            db=int(db or os.environ.get('REDIS_DB', 0)),
            password=password or os.environ.get('REDIS_PASSWORD', None),
            decode_responses=False  
        )
        self._key_prefix = key_prefix or os.environ.get('REDIS_KEY_PREFIX', 'pii_anonymizer:')
        self._expiration_time = int(expiration_time or os.environ.get('REDIS_EXPIRATION_TIME', 3600))
    
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