"""
Unit tests for the Redis cache implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path

# Add parent directory to path to import pii_module
sys.path.append(str(Path(__file__).parent.parent))

from pii_module.redis_cache import RedisCache


class TestRedisCache(unittest.TestCase):
    """Test cases for the RedisCache class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock Redis client
        self.redis_mock = MagicMock()
        
        # Patch the redis.Redis constructor to return our mock
        self.redis_patcher = patch('redis.Redis', return_value=self.redis_mock)
        self.redis_patcher.start()
        
        # Create a RedisCache instance with the mocked Redis client
        self.cache = RedisCache(
            host="localhost",
            port=6379,
            db=0,
            password=None,
            key_prefix="test:",
            expiration_time=3600
        )

    def tearDown(self):
        """Tear down test fixtures"""
        self.redis_patcher.stop()

    def test_get_existing_key(self):
        """Test getting an existing key from the cache"""
        # Set up the mock to return a serialized value
        test_value = {"key": "value"}
        serialized_value = json.dumps(test_value).encode()
        self.redis_mock.get.return_value = serialized_value
        
        # Call the get method
        result = self.cache.get("test_key")
        
        # Verify the result
        self.assertEqual(result, test_value)
        self.redis_mock.get.assert_called_once_with("test:test_key")

    def test_get_nonexistent_key(self):
        """Test getting a nonexistent key from the cache"""
        # Set up the mock to return None
        self.redis_mock.get.return_value = None
        
        # Call the get method
        result = self.cache.get("nonexistent_key")
        
        # Verify the result
        self.assertIsNone(result)
        self.redis_mock.get.assert_called_once_with("test:nonexistent_key")

    def test_get_invalid_json(self):
        """Test getting a key with invalid JSON from the cache"""
        # Set up the mock to return invalid JSON
        self.redis_mock.get.return_value = b"invalid json"
        
        # Call the get method
        result = self.cache.get("invalid_key")
        
        # Verify the result
        self.assertIsNone(result)
        self.redis_mock.get.assert_called_once_with("test:invalid_key")

    def test_set_with_expiration(self):
        """Test setting a key with expiration"""
        # Set up test data
        test_key = "test_key"
        test_value = {"key": "value"}
        
        # Call the set method
        self.cache.set(test_key, test_value)
        
        # Verify the Redis setex method was called with the correct arguments
        self.redis_mock.setex.assert_called_once_with(
            "test:test_key", 
            3600, 
            json.dumps(test_value)
        )

    def test_set_without_expiration(self):
        """Test setting a key without expiration"""
        # Create a cache without expiration
        cache = RedisCache(
            host="localhost",
            port=6379,
            expiration_time=0
        )
        
        # Set up test data
        test_key = "test_key"
        test_value = {"key": "value"}
        
        # Call the set method
        cache.set(test_key, test_value)
        
        # Verify the Redis set method was called with the correct arguments
        self.redis_mock.set.assert_called_once_with(
            "pii_anonymizer:test_key", 
            json.dumps(test_value)
        )

    def test_set_non_serializable_value(self):
        """Test setting a non-serializable value"""
        # Set up test data with a non-serializable value (a function)
        test_key = "test_key"
        test_value = lambda x: x
        
        # Call the set method
        self.cache.set(test_key, test_value)
        
        # Verify no Redis methods were called
        self.redis_mock.setex.assert_not_called()
        self.redis_mock.set.assert_not_called()

    def test_clear(self):
        """Test clearing the cache"""
        # Set up the mock to return some keys
        self.redis_mock.scan.side_effect = [
            (1, [b"test:key1", b"test:key2"]),
            (0, [b"test:key3"])
        ]
        
        # Call the clear method
        self.cache.clear()
        
        # Verify the Redis scan and delete methods were called correctly
        self.assertEqual(self.redis_mock.scan.call_count, 2)
        self.redis_mock.delete.assert_any_call(b"test:key1", b"test:key2")
        self.redis_mock.delete.assert_any_call(b"test:key3")


if __name__ == "__main__":
    unittest.main()