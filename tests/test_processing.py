import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import asyncio

# Add parent directory to path to import modules directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from processing import AsyncPIIProcessingEngine
from core import Language, ProcessingConfig, EntityMatch, AnonymizedEntity
from exceptions import ProcessingError


# Helper function to run async tests
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestAsyncPIIProcessingEngine(unittest.TestCase):
    """Test the AsyncPIIProcessingEngine class"""
    
    def setUp(self):
        """Set up for each test"""
        self.config = ProcessingConfig(
            language=Language.ENGLISH,
            confidence_threshold=0.7,
            cache_enabled=True,
            entities_to_process=["PERSON", "EMAIL_ADDRESS"]
        )
        self.engine = AsyncPIIProcessingEngine(self.config)
    
    def test_initialization(self):
        """Test engine initialization"""
        # Test with cache enabled
        self.assertEqual(self.engine.config.language, Language.ENGLISH)
        self.assertEqual(self.engine.config.confidence_threshold, 0.7)
        self.assertTrue(self.engine.config.cache_enabled)
        
        # Test with cache disabled
        config_no_cache = ProcessingConfig(
            language=Language.ENGLISH,
            confidence_threshold=0.7,
            cache_enabled=False
        )
        engine_no_cache = AsyncPIIProcessingEngine(config_no_cache)
        self.assertFalse(engine_no_cache.config.cache_enabled)
    
    def test_get_fake_generator(self):
        """Test fake generator creation and caching"""
        # Get generator for English
        generator_en = self.engine._get_fake_generator(Language.ENGLISH)
        self.assertEqual(generator_en.language, Language.ENGLISH)
        
        # Get generator for German
        generator_de = self.engine._get_fake_generator(Language.GERMAN)
        self.assertEqual(generator_de.language, Language.GERMAN)
        
        # Verify caching works
        generator_en2 = self.engine._get_fake_generator(Language.ENGLISH)
        self.assertIs(generator_en, generator_en2)  # Should be same instance
    
    def test_get_entities_to_analyze_from_config(self):
        """Test getting entities from config"""
        entities = self.engine._get_entities_to_analyze()
        self.assertEqual(entities, ["PERSON", "EMAIL_ADDRESS"])
    
    @patch('processing.RecognizerFactory')
    def test_get_entities_to_analyze_from_factory(self, mock_factory):
        """Test getting entities from factory when not in config"""
        # Set up mock
        mock_factory.get_all_supported_entities.return_value = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]
        
        # Create engine with no entities specified
        config = ProcessingConfig(language=Language.ENGLISH, entities_to_process=[])
        engine = AsyncPIIProcessingEngine(config)
        
        # Get entities
        entities = engine._get_entities_to_analyze()
        
        # Verify factory was called
        mock_factory.get_all_supported_entities.assert_called_once_with(Language.ENGLISH)
        self.assertEqual(entities, ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"])
    
    def test_filter_entities(self):
        """Test filtering entities by confidence threshold"""
        entities = [
            EntityMatch(entity_type="PERSON", start=0, end=10, text="John Smith", confidence=0.9),
            EntityMatch(entity_type="EMAIL_ADDRESS", start=15, end=30, text="john@example.com", confidence=0.8),
            EntityMatch(entity_type="PHONE_NUMBER", start=35, end=45, text="123-456-7890", confidence=0.6)  # Below threshold
        ]
        
        filtered = self.engine._filter_entities(entities)
        
        # Should only have 2 entities (phone number filtered out)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].entity_type, "PERSON")
        self.assertEqual(filtered[1].entity_type, "EMAIL_ADDRESS")
    
    def test_merge_overlapping_entities(self):
        """Test merging overlapping entities"""
        entities = [
            EntityMatch(entity_type="PERSON", start=0, end=10, text="John Smith", confidence=0.9),
            EntityMatch(entity_type="PERSON", start=5, end=15, text="Smith Jones", confidence=0.8),  # Overlaps with first
            EntityMatch(entity_type="EMAIL_ADDRESS", start=20, end=35, text="john@example.com", confidence=0.7),
            EntityMatch(entity_type="EMAIL_ADDRESS", start=40, end=55, text="jane@example.com", confidence=0.9)
        ]
        
        merged = self.engine._merge_overlapping_entities(entities)
        
        # Should have 3 entities (first two merged)
        self.assertEqual(len(merged), 3)
        self.assertEqual(merged[0].text, "John Smith")  # Higher confidence wins
        self.assertEqual(merged[1].text, "john@example.com")
        self.assertEqual(merged[2].text, "jane@example.com")
    
    def test_anonymize_entities(self):
        """Test anonymizing entities"""
        text = "John Smith's email is john@example.com"
        entities = [
            EntityMatch(entity_type="PERSON", start=0, end=10, text="John Smith", confidence=0.9),
            EntityMatch(entity_type="EMAIL_ADDRESS", start=22, end=38, text="john@example.com", confidence=0.8)
        ]
        
        # Mock the fake generator
        with patch.object(self.engine, '_get_fake_generator') as mock_get_generator:
            mock_generator = MagicMock()
            mock_generator.generate_entity_id.side_effect = lambda entity_type, text: f"{entity_type}_ID"
            mock_generator.generate_fake_value.side_effect = lambda entity_type, text, custom_gen: f"FAKE_{entity_type}"
            mock_get_generator.return_value = mock_generator
            
            # Anonymize
            anonymized_text, entities_map = self.engine._anonymize_entities(text, entities)
            
            # Verify text replacement
            expected_text = "FAKE_PERSON's email is FAKE_EMAIL_ADDRESS"
            self.assertEqual(anonymized_text, expected_text)
            
            # Verify entities map
            self.assertEqual(len(entities_map), 2)
            self.assertIn("PERSON_ID", entities_map)
            self.assertIn("EMAIL_ADDRESS_ID", entities_map)
            
            # Verify entity details
            person_entity = entities_map["PERSON_ID"]
            self.assertEqual(person_entity.original_value, "John Smith")
            self.assertEqual(person_entity.fake_value, "FAKE_PERSON")
            
            email_entity = entities_map["EMAIL_ADDRESS_ID"]
            self.assertEqual(email_entity.original_value, "john@example.com")
            self.assertEqual(email_entity.fake_value, "FAKE_EMAIL_ADDRESS")
    
    @patch('processing.AsyncPIIAnalyzerEngine')
    def test_process_text_async(self, mock_analyzer_class):
        """Test the main async processing method"""
        # Set up mocks
        mock_analyzer_instance = AsyncMock()
        mock_analyzer_instance.__aenter__.return_value = mock_analyzer_instance
        mock_analyzer_instance.__aexit__.return_value = None
        mock_analyzer_instance.analyze_async.return_value = [
            EntityMatch(entity_type="PERSON", start=0, end=10, text="John Smith", confidence=0.9),
            EntityMatch(entity_type="EMAIL_ADDRESS", start=22, end=38, text="john@example.com", confidence=0.8)
        ]
        mock_analyzer_class.return_value = mock_analyzer_instance
        
        # Mock other methods
        with patch.object(self.engine, '_anonymize_entities') as mock_anonymize:
            mock_anonymize.return_value = ("ANONYMIZED TEXT", {"PERSON_ID": MagicMock(), "EMAIL_ID": MagicMock()})
            
            # Process text
            result = run_async(self.engine.process_text_async("John Smith's email is john@example.com"))
            
            # Verify analyzer was called
            mock_analyzer_instance.analyze_async.assert_called_once()
            
            # Verify result
            self.assertEqual(result.anonymized_data, "ANONYMIZED TEXT")
            self.assertEqual(result.total_entities, 2)
            self.assertEqual(result.metadata["language"], "en")
            self.assertEqual(result.metadata["confidence_threshold"], 0.7)
    
    @patch('processing.AsyncPIIAnalyzerEngine')
    def test_process_text_async_error(self, mock_analyzer_class):
        """Test error handling in async processing"""
        # Set up mock to raise exception
        mock_analyzer_instance = AsyncMock()
        mock_analyzer_instance.__aenter__.return_value = mock_analyzer_instance
        mock_analyzer_instance.__aexit__.return_value = None
        mock_analyzer_instance.analyze_async.side_effect = Exception("Test error")
        mock_analyzer_class.return_value = mock_analyzer_instance
        
        # Process text and expect exception
        with self.assertRaises(ProcessingError):
            run_async(self.engine.process_text_async("Test text"))


if __name__ == "__main__":
    unittest.main()