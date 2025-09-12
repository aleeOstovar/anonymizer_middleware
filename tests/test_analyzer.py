import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import asyncio

# Add parent directory to path to import modules directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from analyzer import AsyncPIIAnalyzerEngine
from core import Language, EntityMatch
from cache import ThreadSafeLRUCache, NoCacheStrategy


class TestAsyncPIIAnalyzerEngine(unittest.TestCase):
    """Test the AsyncPIIAnalyzerEngine class"""
    
    def setUp(self):
        """Set up for each test"""
        self.cache = ThreadSafeLRUCache(maxsize=10)
        self.analyzer = AsyncPIIAnalyzerEngine(cache_strategy=self.cache)
    
    def tearDown(self):
        """Clean up after each test"""
        # Ensure the executor is shut down
        if hasattr(self.analyzer, '_executor') and self.analyzer._executor:
            self.analyzer._executor.shutdown(wait=False)
    
    @patch('analyzer.AnalyzerEngine')
    @patch('analyzer.RecognizerRegistry')
    @patch('analyzer.NlpEngineProvider')
    def test_create_analyzer(self, mock_nlp_provider, mock_registry, mock_analyzer_engine):
        """Test analyzer creation"""
        # Setup mocks
        mock_nlp_engine = MagicMock()
        mock_nlp_provider.return_value.create_engine.return_value = mock_nlp_engine
        mock_registry_instance = MagicMock()
        mock_registry.return_value = mock_registry_instance
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        # Call the method
        analyzer = self.analyzer._create_analyzer(Language.ENGLISH)
        
        # Verify the analyzer was created correctly
        mock_nlp_provider.return_value.create_engine.assert_called_once()
        mock_registry.assert_called_once()
        # Don't check parameter order, just check that the correct parameters were passed
        mock_analyzer_engine.assert_called_once()
        call_kwargs = mock_analyzer_engine.call_args[1]
        self.assertEqual(call_kwargs.get('nlp_engine'), mock_nlp_engine)
        self.assertEqual(call_kwargs.get('registry'), mock_registry_instance)
        self.assertEqual(analyzer, mock_analyzer_instance)
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        text = "John Smith lives in New York"
        language = Language.ENGLISH
        entities = ["PERSON", "LOCATION"]
        
        # Generate the key
        key = self.analyzer._get_cache_key(text, language, entities)
        
        # Verify it's a string and contains the language code
        self.assertIsInstance(key, str)
        self.assertIn(language.value, key)
        
        # Verify different inputs produce different keys
        different_text_key = self.analyzer._get_cache_key("Different text", language, entities)
        different_lang_key = self.analyzer._get_cache_key(text, Language.GERMAN, entities)
        different_entities_key = self.analyzer._get_cache_key(text, language, ["PERSON"])
        
        self.assertNotEqual(key, different_text_key)
        self.assertNotEqual(key, different_lang_key)
        self.assertNotEqual(key, different_entities_key)
    
    @patch('analyzer.AsyncPIIAnalyzerEngine._get_or_create_analyzer')
    async def test_analyze_async_with_cache_hit(self, mock_get_analyzer):
        """Test analyze_async with cache hit"""
        # Setup
        text = "John Smith lives in New York"
        language = Language.ENGLISH
        entities = ["PERSON", "LOCATION"]
        expected_result = [
            EntityMatch(entity_type="PERSON", start=0, end=10, text="John Smith", confidence=0.9)
        ]
        
        # Set up cache hit
        cache_key = self.analyzer._get_cache_key(text, language, entities)
        self.cache.set(cache_key, expected_result)
        
        # Create async context
        async with self.analyzer:
            # Call the method
            result = await self.analyzer.analyze_async(text, language, entities)
            
            # Verify result and that analyzer wasn't called
            self.assertEqual(result, expected_result)
            mock_get_analyzer.assert_not_called()
    
    @patch('analyzer.AsyncPIIAnalyzerEngine._analyze_sync_internal')
    async def test_analyze_async_with_cache_miss(self, mock_analyze_internal):
        """Test analyze_async with cache miss"""
        # Setup
        text = "John Smith lives in New York"
        language = Language.ENGLISH
        entities = ["PERSON", "LOCATION"]
        expected_result = [
            EntityMatch(entity_type="PERSON", start=0, end=10, text="John Smith", confidence=0.9)
        ]
        mock_analyze_internal.return_value = expected_result
        
        # Create async context
        async with self.analyzer:
            # Call the method
            result = await self.analyzer.analyze_async(text, language, entities)
            
            # Verify result and that analyzer was called
            self.assertEqual(result, expected_result)
            mock_analyze_internal.assert_called_once_with(text, language, entities)
            
            # Verify result was cached
            cache_key = self.analyzer._get_cache_key(text, language, entities)
            cached_result = self.cache.get(cache_key)
            self.assertEqual(cached_result, expected_result)
    
    def test_analyze_sync_internal(self):
        """Test the internal synchronous analysis method"""
        # This would require more extensive mocking of the presidio analyzer
        # For now, we'll just test the error handling
        with patch('analyzer.AsyncPIIAnalyzerEngine._get_or_create_analyzer') as mock_get_analyzer:
            # Setup mock to raise an exception
            mock_get_analyzer.side_effect = Exception("Test error")
            
            # Call the method and expect an AnalysisError
            from exceptions import AnalysisError
            with self.assertRaises(AnalysisError):
                self.analyzer._analyze_sync_internal(
                    "Test text", Language.ENGLISH, ["PERSON"]
                )


# Helper function to run async tests
def run_async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Modify the test methods to be runnable with unittest
def async_test(async_func):
    def wrapper(*args, **kwargs):
        return run_async_test(async_func(*args, **kwargs))
    return wrapper

# Apply the decorator to the async test methods
TestAsyncPIIAnalyzerEngine.test_analyze_async_with_cache_hit = async_test(TestAsyncPIIAnalyzerEngine.test_analyze_async_with_cache_hit)
TestAsyncPIIAnalyzerEngine.test_analyze_async_with_cache_miss = async_test(TestAsyncPIIAnalyzerEngine.test_analyze_async_with_cache_miss)


if __name__ == "__main__":
    unittest.main()