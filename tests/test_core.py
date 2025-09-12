import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path to import modules directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core import Language, EntityMatch, AnonymizedEntity, ProcessingConfig, ProcessingResult


class TestLanguage(unittest.TestCase):
    """Test the Language enum"""
    
    def test_language_values(self):
        """Test language enum values"""
        self.assertEqual(Language.ENGLISH.value, "en")
        self.assertEqual(Language.GERMAN.value, "de")


class TestEntityMatch(unittest.TestCase):
    """Test the EntityMatch class"""
    
    def test_valid_entity_match(self):
        """Test creating a valid EntityMatch"""
        entity = EntityMatch(
            entity_type="PERSON",
            start=0,
            end=10,
            text="John Smith",
            confidence=0.8
        )
        
        self.assertEqual(entity.entity_type, "PERSON")
        self.assertEqual(entity.start, 0)
        self.assertEqual(entity.end, 10)
        self.assertEqual(entity.text, "John Smith")
        self.assertEqual(entity.confidence, 0.8)
    
    def test_invalid_position(self):
        """Test validation for invalid position"""
        with self.assertRaises(ValueError):
            EntityMatch(
                entity_type="PERSON",
                start=10,  # Start greater than end
                end=5,
                text="John Smith",
                confidence=0.8
            )
        
        with self.assertRaises(ValueError):
            EntityMatch(
                entity_type="PERSON",
                start=-1,  # Negative start
                end=5,
                text="John Smith",
                confidence=0.8
            )
    
    def test_invalid_confidence(self):
        """Test validation for invalid confidence"""
        with self.assertRaises(ValueError):
            EntityMatch(
                entity_type="PERSON",
                start=0,
                end=10,
                text="John Smith",
                confidence=1.5  # Greater than 1
            )
        
        with self.assertRaises(ValueError):
            EntityMatch(
                entity_type="PERSON",
                start=0,
                end=10,
                text="John Smith",
                confidence=-0.1  # Negative confidence
            )
    
    def test_to_dict(self):
        """Test to_dict method"""
        entity = EntityMatch(
            entity_type="PERSON",
            start=0,
            end=10,
            text="John Smith",
            confidence=0.8
        )
        
        expected_dict = {
            "entity_type": "PERSON",
            "start": 0,
            "end": 10,
            "text": "John Smith",
            "confidence": 0.8
        }
        
        self.assertEqual(entity.to_dict(), expected_dict)


class TestAnonymizedEntity(unittest.TestCase):
    """Test the AnonymizedEntity class"""
    
    def test_anonymized_entity(self):
        """Test creating an AnonymizedEntity"""
        entity = AnonymizedEntity(
            entity_id="123",
            original_value="John Smith",
            entity_type="PERSON",
            fake_value="Jane Doe",
            confidence=0.9,
            metadata={"source": "test"}
        )
        
        self.assertEqual(entity.entity_id, "123")
        self.assertEqual(entity.original_value, "John Smith")
        self.assertEqual(entity.entity_type, "PERSON")
        self.assertEqual(entity.fake_value, "Jane Doe")
        self.assertEqual(entity.confidence, 0.9)
        self.assertEqual(entity.metadata, {"source": "test"})
    
    def test_to_dict(self):
        """Test to_dict method"""
        entity = AnonymizedEntity(
            entity_id="123",
            original_value="John Smith",
            entity_type="PERSON",
            fake_value="Jane Doe",
            confidence=0.9,
            metadata={"source": "test"}
        )
        
        expected_dict = {
            "original_value": "John Smith",
            "entity_type": "PERSON",
            "fake_value": "Jane Doe",
            "confidence": 0.9,
            "metadata": {"source": "test"}
        }
        
        self.assertEqual(entity.to_dict(), expected_dict)
    
    def test_default_metadata(self):
        """Test default metadata"""
        entity = AnonymizedEntity(
            entity_id="123",
            original_value="John Smith",
            entity_type="PERSON",
            fake_value="Jane Doe",
            confidence=0.9
        )
        
        self.assertEqual(entity.metadata, None)
        self.assertEqual(entity.to_dict()["metadata"], {})


class TestProcessingConfig(unittest.TestCase):
    """Test the ProcessingConfig class"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = ProcessingConfig()
        
        self.assertEqual(config.language, Language.ENGLISH)
        self.assertEqual(config.entities_to_process, None)
        self.assertEqual(config.confidence_threshold, 0.5)
        self.assertTrue(config.preserve_format)
        self.assertEqual(config.custom_fake_generators, None)
        self.assertEqual(config.max_workers, 4)
        self.assertEqual(config.chunk_size, 2000)
        self.assertTrue(config.cache_enabled)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = ProcessingConfig(
            language=Language.GERMAN,
            entities_to_process=["PERSON", "LOCATION"],
            confidence_threshold=0.7,
            preserve_format=False,
            max_workers=8,
            chunk_size=1000,
            cache_enabled=False
        )
        
        self.assertEqual(config.language, Language.GERMAN)
        self.assertEqual(config.entities_to_process, ["PERSON", "LOCATION"])
        self.assertEqual(config.confidence_threshold, 0.7)
        self.assertFalse(config.preserve_format)
        self.assertEqual(config.max_workers, 8)
        self.assertEqual(config.chunk_size, 1000)
        self.assertFalse(config.cache_enabled)
    
    def test_invalid_confidence_threshold(self):
        """Test validation for invalid confidence threshold"""
        with self.assertRaises(ValueError):
            ProcessingConfig(confidence_threshold=1.5)  # Greater than 1
        
        with self.assertRaises(ValueError):
            ProcessingConfig(confidence_threshold=-0.1)  # Negative
    
    def test_invalid_max_workers(self):
        """Test validation for invalid max_workers"""
        with self.assertRaises(ValueError):
            ProcessingConfig(max_workers=0)  # Must be at least 1
        
        with self.assertRaises(ValueError):
            ProcessingConfig(max_workers=-1)  # Negative
    
    def test_invalid_chunk_size(self):
        """Test validation for invalid chunk_size"""
        with self.assertRaises(ValueError):
            ProcessingConfig(chunk_size=99)  # Must be at least 100
        
        with self.assertRaises(ValueError):
            ProcessingConfig(chunk_size=-1)  # Negative


class TestProcessingResult(unittest.TestCase):
    """Test the ProcessingResult class"""
    
    def test_processing_result(self):
        """Test creating a ProcessingResult"""
        anonymized_entity = AnonymizedEntity(
            entity_id="123",
            original_value="John Smith",
            entity_type="PERSON",
            fake_value="Jane Doe",
            confidence=0.9
        )
        
        result = ProcessingResult(
            anonymized_data="Hello, Jane Doe",
            entities_map={"123": anonymized_entity},
            metadata={"source": "test"},
            processing_time=0.5,
            cache_hits=2,
            total_entities=1
        )
        
        self.assertEqual(result.anonymized_data, "Hello, Jane Doe")
        self.assertEqual(result.entities_map, {"123": anonymized_entity})
        self.assertEqual(result.metadata, {"source": "test"})
        self.assertEqual(result.processing_time, 0.5)
        self.assertEqual(result.cache_hits, 2)
        self.assertEqual(result.total_entities, 1)
    
    def test_default_values(self):
        """Test default values"""
        anonymized_entity = AnonymizedEntity(
            entity_id="123",
            original_value="John Smith",
            entity_type="PERSON",
            fake_value="Jane Doe",
            confidence=0.9
        )
        
        result = ProcessingResult(
            anonymized_data="Hello, Jane Doe",
            entities_map={"123": anonymized_entity}
        )
        
        self.assertEqual(result.metadata, {})
        self.assertEqual(result.processing_time, 0.0)
        self.assertEqual(result.cache_hits, 0)
        self.assertEqual(result.total_entities, 0)


if __name__ == "__main__":
    unittest.main()