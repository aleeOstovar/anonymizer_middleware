import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fake_generator import FakeDataGenerator
from core import Language


class TestFakeDataGenerator(unittest.TestCase):
    """Test the FakeDataGenerator class"""
    
    def setUp(self):
        """Set up for each test"""
        self.english_generator = FakeDataGenerator(Language.ENGLISH)
        self.german_generator = FakeDataGenerator(Language.GERMAN)
    
    def test_create_faker_instance(self):
        """Test Faker instance creation with correct locale"""
        # Test English locale
        self.assertIn('en_US', self.english_generator.fake.locales)
        
        # Test German locale
        self.assertIn('de_DE', self.german_generator.fake.locales)
    
    def test_generate_entity_id(self):
        """Test entity ID generation"""
        entity_type = "PERSON"
        original_value = "John Smith"
        
        entity_id = self.english_generator.generate_entity_id(entity_type, original_value)
        
        self.assertTrue(re.match(r'^PERSON_[0-9a-f]{8}$', entity_id))
        
        entity_id2 = self.english_generator.generate_entity_id(entity_type, original_value)
        self.assertEqual(entity_id, entity_id2)
        
        different_id = self.english_generator.generate_entity_id(entity_type, "Jane Doe")
        self.assertNotEqual(entity_id, different_id)
    
    def test_generate_default_value(self):
        """Test default value generation"""
        entity_type = "UNKNOWN_TYPE"
        original_value = "Test Value"

        default_value = self.english_generator._generate_default_value(entity_type, original_value)
        

        self.assertTrue(re.match(r'^\[UNKNOWN_TYPE_[0-9a-f]{8}\]$', default_value))
    
    def test_generate_fake_value_with_custom_generator(self):
        """Test fake value generation with custom generator"""
        custom_generator = lambda x: f"CUSTOM_{x}"
        
        fake_value = self.english_generator.generate_fake_value(
            "PERSON", "John Smith", custom_generator
        )
        

        self.assertEqual(fake_value, "CUSTOM_John Smith")
    
    def test_generate_fake_value_with_builtin_generator(self):
        """Test fake value generation with built-in generator"""
        person_value = self.english_generator.generate_fake_value("PERSON", "John Smith")
        email_value = self.english_generator.generate_fake_value("EMAIL_ADDRESS", "john@example.com")
        phone_value = self.english_generator.generate_fake_value("PHONE_NUMBER", "123-456-7890")
        
        self.assertTrue(person_value)
        self.assertNotEqual(person_value, "John Smith")
        
        self.assertTrue(email_value)
        self.assertNotEqual(email_value, "john@example.com")
        self.assertTrue('@' in email_value)  # Basic email format check
        
        self.assertTrue(phone_value)
        self.assertNotEqual(phone_value, "123-456-7890")
    
    def test_generate_fake_value_with_unknown_type(self):
        """Test fake value generation with unknown entity type"""
        original_value = "Test Value"
        

        fake_value = self.english_generator.generate_fake_value("UNKNOWN_TYPE", original_value)

        self.assertTrue(re.match(r'^\[UNKNOWN_TYPE_[0-9a-f]{8}\]$', fake_value))
    
    def test_language_specific_generators(self):
        """Test language-specific generators"""

        with patch.object(self.german_generator, '_create_german_generators') as mock_german_gen:
            mock_german_gen.return_value = {"GERMAN_ID": lambda: "DE12345"}

            self.german_generator._generators = self.german_generator._create_generators()

            fake_value = self.german_generator.generate_fake_value("GERMAN_ID", "Original")
            mock_german_gen.assert_called_once()
            self.assertEqual(fake_value, "DE12345")
        
        with patch.object(self.english_generator, '_create_english_generators') as mock_english_gen:
            mock_english_gen.return_value = {"ENGLISH_ID": lambda: "EN12345"}

            self.english_generator._generators = self.english_generator._create_generators()

            fake_value = self.english_generator.generate_fake_value("ENGLISH_ID", "Original")
            mock_english_gen.assert_called_once()
            self.assertEqual(fake_value, "EN12345")


if __name__ == "__main__":
    unittest.main()