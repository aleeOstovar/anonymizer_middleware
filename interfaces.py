"""
Interfaces and protocols for the PII anonymizer module.
Implements the Interface Segregation Principle from SOLID.
"""

from typing import List, Any, Optional, Callable, Protocol
from abc import ABC, abstractmethod

from core import Language, EntityMatch


class IAnalyzer(Protocol):
    """Interface for PII analyzers (Interface Segregation Principle)"""
    
    async def analyze_async(self, text: str, language: Language, entities: List[str]) -> List[EntityMatch]:
        """Analyze text asynchronously for PII entities"""
        ...
    
    def analyze_sync(self, text: str, language: Language, entities: List[str]) -> List[EntityMatch]:
        """Analyze text synchronously for PII entities"""
        ...


class IRecognizer(Protocol):
    """Interface for recognizers"""
    
    def get_recognizers(self) -> List[Any]:
        """Get list of pattern recognizers"""
        ...
    
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types"""
        ...


class IFakeDataGenerator(Protocol):
    """Interface for fake data generation"""
    
    def generate_fake_value(self, entity_type: str, original_value: str, custom_generator: Optional[Callable] = None) -> str:
        """Generate fake value for an entity"""
        ...
    
    def generate_entity_id(self, entity_type: str, original_value: str) -> str:
        """Generate unique entity ID"""
        ...


class ICacheStrategy(Protocol):
    """Interface for caching strategies"""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        ...
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        ...
    
    def clear(self) -> None:
        """Clear cache"""
        ...