"""
Integration tests for Redis cache with PII anonymizer.
"""

import unittest
import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import pii_module
sys.path.append(str(Path(__file__).parent.parent))

from pii_module import (
    ArchitecturalPIIAnonymizer,
    Language,
    RedisCache
)


class TestRedisIntegration(unittest.TestCase):
    """Integration tests for Redis cache with PII anonymizer"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock Redis
        self.redis_patcher = patch('redis.Redis')
        self.mock_redis_class = self.redis_patcher.start()
        self.mock_redis = self.mock_redis_class.return_value
        
        # Configure Redis mock for get/set operations
        self.mock_redis.get.return_value = None  # Initially cache is empty
        
        # Create Redis cache
        self.redis_cache = RedisCache(
            host="localhost",
            port=6379,
            key_prefix="test_integration:",
            expiration_time=3600
        )
        
        # Create anonymizer
        self.anonymizer = ArchitecturalPIIAnonymizer()

    def tearDown(self):
        """Tear down test fixtures"""
        self.redis_patcher.stop()

    def test_cache_integration(self):
        """Test Redis cache integration with PII anonymizer"""
        # Test text with PII
        test_text = "My email is john.doe@example.com and my phone is +1 555-123-4567"
        
        # Run the test using asyncio
        result = asyncio.run(self._run_anonymization_test(test_text))
        
        # Verify the anonymization worked
        self.assertNotEqual(result.anonymized_data, test_text)
        self.assertNotIn("john.doe@example.com", result.anonymized_data)
        self.assertNotIn("+1 555-123-4567", result.anonymized_data)
        
        # Verify Redis was used
        self.mock_redis.get.assert_called()
        self.mock_redis.setex.assert_called()

    def test_cache_hit(self):
        """Test Redis cache hit"""
        # Test text with PII
        test_text = "My email is jane.doe@example.com"
        
        # Configure Redis mock to return a cached result
        cached_result = {
            "anonymized_data": "My email is [EMAIL]",
            "entities_map": {"jane.doe@example.com": {"entity_type": "EMAIL_ADDRESS"}}
        }
        import json
        self.mock_redis.get.return_value = json.dumps(cached_result).encode()
        
        # Run the test using asyncio
        result = asyncio.run(self._run_anonymization_test(test_text))
        
        # Verify the cached result was used
        self.assertEqual(result.anonymized_data, "My email is [EMAIL]")
        
        # Verify Redis get was called but set was not
        self.mock_redis.get.assert_called()
        self.mock_redis.setex.assert_not_called()

    async def _run_anonymization_test(self, text):
        """Helper method to run anonymization with Redis cache"""
        # Patch the analyzer to use our Redis cache
        with patch('pii_module.analyzer.AsyncPIIAnalyzerEngine.__init__', return_value=None) as mock_init:
            with patch('pii_module.analyzer.AsyncPIIAnalyzerEngine._cache', self.redis_cache):
                with patch('pii_module.analyzer.AsyncPIIAnalyzerEngine.__aenter__', return_value=MagicMock()) as mock_enter:
                    with patch('pii_module.analyzer.AsyncPIIAnalyzerEngine.__aexit__', return_value=None) as mock_exit:
                        with patch('pii_module.analyzer.AsyncPIIAnalyzerEngine.analyze_async') as mock_analyze:
                            # Configure the mock to return some entities
                            from pii_module.core import EntityMatch
                            mock_analyze.return_value = [
                                EntityMatch(
                                    entity_type="EMAIL_ADDRESS",
                                    text="john.doe@example.com",
                                    start_pos=12,
                                    end_pos=31,
                                    confidence=0.9
                                ),
                                EntityMatch(
                                    entity_type="PHONE_NUMBER",
                                    text="+1 555-123-4567",
                                    start_pos=41,
                                    end_pos=56,
                                    confidence=0.8
                                )
                            ]
                            
                            # Run the anonymization
                            result = await self.anonymizer.anonymize_text_async(
                                text=text,
                                language=Language.ENGLISH,
                                cache_enabled=True
                            )
                            
                            return result


if __name__ == "__main__":
    unittest.main()