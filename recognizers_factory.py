"""
Factory pattern for creating recognizers based on language.
Implements the Factory pattern with singleton-like caching.
"""

import weakref
from typing import List

from core import Language
from exceptions import ConfigurationError
from recognizers_base import BaseRecognizer
from recognizers_english import EnglishRecognizers
from recognizers_german import GermanRecognizers


class RecognizerFactory:
    """Factory for creating recognizers (Factory Pattern)"""
    
    _recognizer_classes = {
        Language.ENGLISH: EnglishRecognizers,
        Language.GERMAN: GermanRecognizers
    }
    
    _instances = weakref.WeakValueDictionary()
    
    @classmethod
    def create_recognizer(cls, language: Language) -> BaseRecognizer:
        """Create or reuse recognizer instance"""
        if language in cls._instances:
            return cls._instances[language]
        
        if language not in cls._recognizer_classes:
            raise ConfigurationError(f"Unsupported language: {language}")
        
        recognizer = cls._recognizer_classes[language]()
        cls._instances[language] = recognizer
        return recognizer
    
    @classmethod
    def get_all_supported_entities(cls, language: Language) -> List[str]:
        """Get all supported entities for a language"""
        base_entities = [
            "CREDIT_CARD", "DATE_TIME", "EMAIL_ADDRESS", "IBAN_CODE",
            "IP_ADDRESS", "LOCATION", "PERSON", "PHONE_NUMBER", "URL"
        ]
        recognizer = cls.create_recognizer(language)
        return base_entities + recognizer.get_supported_entities()