import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from redis_cache import RedisCache


class TestRedisCache(unittest.TestCase):
    """Test the RedisCache class"""
    
    def setUp(self):
        """Set up for each test with mocked Redis client"""
        self.redis_mock = MagicMock()
        self.patcher = patch('redis_cache.redis.Redis', return_value=self.redis_mock)
        self.patcher.start()
        
        self.cache = RedisCache()

        from redis_cache import redis
        redis.Redis.assert_called_once_with(
            host="localhost",
            port=6379,
            db=0,
            password=None,
            decode_responses=False
        )
    
    def tearDown(self):
        """Clean up after each test"""
        self.patcher.stop()
    
    def test_initialization_with_custom_params(self):
        """Test initialization with custom parameters"""
        from redis_cache import redis
        redis.Redis.reset_mock()

        custom_cache = RedisCache(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            key_prefix="custom:",
            expiration_time=7200
        )

        redis.Redis.assert_called_once_with(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            decode_responses=False
        )

        self.assertEqual(custom_cache._key_prefix, "custom:")
        self.assertEqual(custom_cache._expiration_time, 7200)
    
    def test_format_key(self):
        """Test key formatting with prefix"""

        self.assertEqual(self.cache._format_key("test_key"), "pii_anonymizer:test_key")
        

        custom_cache = RedisCache(key_prefix="custom:")
        self.assertEqual(custom_cache._format_key("test_key"), "custom:test_key")
    
    def test_get_existing_value(self):
        """Test getting an existing value from cache"""

        test_data = {"name": "John", "age": 30}
        self.redis_mock.get.return_value = json.dumps(test_data).encode()

        result = self.cache.get("test_key")
        

        self.redis_mock.get.assert_called_once_with("pii_anonymizer:test_key")

        self.assertEqual(result, test_data)
    
    def test_get_nonexistent_value(self):
        """Test getting a nonexistent value from cache"""

        self.redis_mock.get.return_value = None
        

        result = self.cache.get("nonexistent_key")

        self.redis_mock.get.assert_called_once_with("pii_anonymizer:nonexistent_key")

        self.assertIsNone(result)
    
    def test_get_invalid_json(self):
        """Test getting a value that can't be deserialized"""

        self.redis_mock.get.return_value = b"invalid json"

        result = self.cache.get("invalid_key")
        

        self.redis_mock.get.assert_called_once_with("pii_anonymizer:invalid_key")

        self.assertIsNone(result)
    
    def test_set_with_expiration(self):
        """Test setting a value with expiration"""
        # Set value in cache
        test_data = {"name": "John", "age": 30}
        self.cache.set("test_key", test_data)
        
        # Verify Redis setex was called with correct parameters
        self.redis_mock.setex.assert_called_once_with(
            "pii_anonymizer:test_key",
            3600,  # Default expiration time
            json.dumps(test_data)
        )
    
    def test_set_without_expiration(self):
        """Test setting a value without expiration"""
        # Create cache with no expiration
        no_expiration_cache = RedisCache(expiration_time=0)
        
        # Set value in cache
        test_data = {"name": "John", "age": 30}
        no_expiration_cache.set("test_key", test_data)
        
        # Verify Redis set was called with correct parameters
        self.redis_mock.set.assert_called_once_with(
            "pii_anonymizer:test_key",
            json.dumps(test_data)
        )
    
    def test_set_non_serializable_value(self):
        """Test setting a value that can't be serialized"""
        # Create a non-serializable object (a function)
        non_serializable = lambda x: x
        
        # Set value in cache
        self.cache.set("test_key", non_serializable)
        
        # Verify Redis set was not called
        self.redis_mock.setex.assert_not_called()
        self.redis_mock.set.assert_not_called()
    
    def test_clear(self):
        """Test clearing all keys with prefix"""
        # Set up mock to return keys in batches
        self.redis_mock.scan.side_effect = [
            (1, [b"pii_anonymizer:key1", b"pii_anonymizer:key2"]),
            (0, [b"pii_anonymizer:key3"])
        ]
        
        # Clear cache
        self.cache.clear()
        
        # Verify Redis scan was called with correct pattern
        self.redis_mock.scan.assert_any_call(0, "pii_anonymizer:*", 100)
        self.redis_mock.scan.assert_any_call(1, "pii_anonymizer:*", 100)
        
        # Verify Redis delete was called with correct keys
        self.redis_mock.delete.assert_any_call(b"pii_anonymizer:key1", b"pii_anonymizer:key2")
        self.redis_mock.delete.assert_any_call(b"pii_anonymizer:key3")


if __name__ == "__main__":
    unittest.main()