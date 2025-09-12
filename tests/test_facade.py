import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import asyncio

# Add parent directory to path to import modules directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from facade import ArchitecturalPIIAnonymizer
from core import Language, ProcessingConfig, ProcessingResult, AnonymizedEntity


# Helper function to run async tests
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestArchitecturalPIIAnonymizer(unittest.TestCase):
    """Test the ArchitecturalPIIAnonymizer class"""
    
    def setUp(self):
        """Set up for each test"""
        self.anonymizer = ArchitecturalPIIAnonymizer()
    
    @patch('facade.AsyncPIIProcessingEngine')
    def test_anonymize_text_async(self, mock_engine_class):
        """Test async anonymization"""
        # Set up mock
        mock_engine_instance = MagicMock()
        mock_engine_instance.process_text_async = AsyncMock()
        mock_engine_instance.process_text_async.return_value = ProcessingResult(
            anonymized_data="ANONYMIZED TEXT",
            entities_map={"PERSON_1": MagicMock()},
            processing_time=0.1,
            total_entities=1,
            metadata={"language": "ENGLISH"}
        )
        mock_engine_class.return_value = mock_engine_instance
        
        # Call anonymize_text_async
        result = run_async(self.anonymizer.anonymize_text_async(
            text="John Smith",
            language=Language.ENGLISH,
            entities_to_anonymize=["PERSON"],
            confidence_threshold=0.7,
            cache_enabled=True
        ))
        
        # Verify engine was created with correct config
        mock_engine_class.assert_called_once()
        config = mock_engine_class.call_args[0][0]
        self.assertEqual(config.language, Language.ENGLISH)
        self.assertEqual(config.entities_to_process, ["PERSON"])
        self.assertEqual(config.confidence_threshold, 0.7)
        self.assertTrue(config.cache_enabled)
        
        # Verify process_text_async was called
        mock_engine_instance.process_text_async.assert_called_once_with("John Smith")
        
        # Verify result
        self.assertEqual(result.anonymized_data, "ANONYMIZED TEXT")
        self.assertEqual(result.total_entities, 1)
    
    @patch('facade.asyncio.run')
    def test_anonymize_text_sync(self, mock_run):
        """Test synchronous anonymization wrapper"""
        # Set up mock
        mock_result = ProcessingResult(
            anonymized_data="ANONYMIZED TEXT",
            entities_map={"PERSON_1": MagicMock()},
            processing_time=0.1,
            total_entities=1,
            metadata={"language": "ENGLISH"}
        )
        mock_run.return_value = mock_result
        
        # Call anonymize_text_sync
        result = self.anonymizer.anonymize_text_sync(
            text="John Smith",
            language=Language.ENGLISH,
            entities_to_anonymize=["PERSON"]
        )
        
        # Verify asyncio.run was called
        mock_run.assert_called_once()
        
        # Verify result
        self.assertEqual(result, mock_result)
    
    @patch('facade.DeanonymizationService')
    def test_deanonymize_text(self, mock_deanonymization_service):
        """Test deanonymization"""
        # Set up mock
        mock_service_instance = MagicMock()
        mock_service_instance.deanonymize_text.return_value = ProcessingResult(
            anonymized_data="John Smith",  # Now deanonymized
            entities_map={"PERSON_1": MagicMock()},
            processing_time=0.1,
            total_entities=1,
            metadata={"language": "ENGLISH"}
        )
        mock_deanonymization_service.return_value = mock_service_instance
        
        # Create anonymizer with mocked service
        anonymizer = ArchitecturalPIIAnonymizer()
        
        # Call deanonymize_text
        anonymized_text = "ANONYMIZED TEXT"
        entities_map = {"PERSON_1": AnonymizedEntity(
            entity_id="PERSON_1",
            original_value="John Smith",
            entity_type="PERSON",
            fake_value="ANONYMIZED TEXT",
            confidence=0.9
        )}
        
        result = anonymizer.deanonymize_text(anonymized_text, entities_map)
        
        # Verify deanonymize_text was called
        mock_service_instance.deanonymize_text.assert_called_once_with(anonymized_text, entities_map)
        
        # Verify result
        self.assertEqual(result.anonymized_data, "John Smith")
    
    @patch('facade.AsyncPIIAnalyzerEngine')
    @patch('facade.RecognizerFactory')
    def test_analyze_only_async(self, mock_factory, mock_analyzer_class):
        """Test async analysis without anonymization"""
        # Set up mocks
        mock_factory.get_all_supported_entities.return_value = ["PERSON", "EMAIL_ADDRESS"]
        
        mock_analyzer_instance = AsyncMock()
        mock_analyzer_instance.__aenter__.return_value = mock_analyzer_instance
        mock_analyzer_instance.__aexit__.return_value = None
        
        entity1 = MagicMock()
        entity1.confidence = 0.9
        entity1.to_dict.return_value = {"entity_type": "PERSON", "text": "John Smith"}
        
        entity2 = MagicMock()
        entity2.confidence = 0.4  # Below threshold
        entity2.to_dict.return_value = {"entity_type": "EMAIL_ADDRESS", "text": "john@example.com"}
        
        mock_analyzer_instance.analyze_async.return_value = [entity1, entity2]
        mock_analyzer_class.return_value = mock_analyzer_instance
        
        # Call analyze_only_async
        result = run_async(self.anonymizer.analyze_only_async(
            text="John Smith's email is john@example.com",
            language=Language.ENGLISH,
            confidence_threshold=0.7
        ))
        
        # Verify analyzer was created
        mock_analyzer_class.assert_called_once()
        
        # Verify analyze_async was called
        mock_analyzer_instance.analyze_async.assert_called_once()
        
        # Verify result (only entity1 should be included due to confidence threshold)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"entity_type": "PERSON", "text": "John Smith"})
    
    @patch('facade.asyncio.run')
    def test_analyze_only_sync(self, mock_run):
        """Test synchronous analysis wrapper"""
        # Set up mock
        mock_result = [{"entity_type": "PERSON", "text": "John Smith"}]
        mock_run.return_value = mock_result
        
        # Call analyze_only_sync
        result = self.anonymizer.analyze_only_sync(
            text="John Smith",
            language=Language.ENGLISH
        )
        
        # Verify asyncio.run was called
        mock_run.assert_called_once()
        
        # Verify result
        self.assertEqual(result, mock_result)
    
    @patch('facade.RecognizerFactory')
    def test_get_supported_entities(self, mock_factory):
        """Test getting supported entities"""
        # Set up mock
        mock_factory.get_all_supported_entities.return_value = ["PERSON", "EMAIL_ADDRESS"]
        
        # Call get_supported_entities
        result = self.anonymizer.get_supported_entities(Language.ENGLISH)
        
        # Verify factory was called
        mock_factory.get_all_supported_entities.assert_called_once_with(Language.ENGLISH)
        
        # Verify result
        self.assertEqual(result, ["PERSON", "EMAIL_ADDRESS"])
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        # Call get_supported_languages
        result = self.anonymizer.get_supported_languages()
        
        # Verify result contains expected languages
        self.assertIn("en", result)
        self.assertIn("de", result)
    
    @patch('facade.AsyncPIIProcessingEngine')
    def test_batch_processing_context(self, mock_engine_class):
        """Test batch processing context manager"""
        # Set up mock
        mock_engine_instance = MagicMock()
        mock_engine_class.return_value = mock_engine_instance
        
        # Create config
        config = ProcessingConfig(language=Language.ENGLISH)
        
        # Use context manager
        async def test_context():
            async with self.anonymizer.batch_processing_context(config) as engine:
                self.assertEqual(engine, mock_engine_instance)
        
        # Run async test
        run_async(test_context())
        
        # Verify engine was created with correct config
        mock_engine_class.assert_called_once_with(config)


if __name__ == "__main__":
    unittest.main()