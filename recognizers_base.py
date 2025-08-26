"""
Base recognizer classes implementing the Open/Closed Principle.
Abstract base class for all recognizers with common functionality.
"""

from abc import ABC, abstractmethod
from typing import List
from presidio_analyzer import PatternRecognizer


class BaseRecognizer(ABC):
    """Abstract base for all recognizers"""
    
    def __init__(self):
        self._recognizers = None
        self._supported_entities = None
    
    @abstractmethod
    def _create_recognizers(self) -> List[PatternRecognizer]:
        """Create recognizers - implemented by subclasses"""
        pass
    
    @abstractmethod
    def _get_entity_types(self) -> List[str]:
        """Get supported entity types - implemented by subclasses"""
        pass
    
    def get_recognizers(self) -> List[PatternRecognizer]:
        """Lazy initialization of recognizers"""
        if self._recognizers is None:
            self._recognizers = self._create_recognizers()
        return self._recognizers
    
    def get_supported_entities(self) -> List[str]:
        """Lazy initialization of supported entities"""
        if self._supported_entities is None:
            self._supported_entities = self._get_entity_types()
        return self._supported_entities