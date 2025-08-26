"""
Core types and data classes for the PII anonymizer module.
Contains the main value objects and configuration classes.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Union

""" 
Import the main facade here to make it available from core
add this at the end of the file to avoid circular imports
"""


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    GERMAN = "de"


@dataclass(frozen=True)
class EntityMatch:
    """Immutable representation of a detected PII entity"""
    entity_type: str
    start: int
    end: int
    text: str
    confidence: float

    def __post_init__(self):
        if self.start < 0 or self.end <= self.start:
            raise ValueError("Invalid entity position")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence
        }


@dataclass(frozen=True)
class AnonymizedEntity:
    """Immutable representation of an anonymized entity"""
    entity_id: str
    original_value: str
    entity_type: str
    fake_value: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_value": self.original_value,
            "entity_type": self.entity_type,
            "fake_value": self.fake_value,
            "confidence": self.confidence,
            "metadata": self.metadata or {}
        }


@dataclass
class ProcessingConfig:
    """Configuration for anonymization processing with validation"""
    language: Language = Language.ENGLISH
    entities_to_process: Optional[List[str]] = None
    confidence_threshold: float = 0.5
    preserve_format: bool = True
    custom_fake_generators: Optional[Dict[str, Callable]] = None
    max_workers: int = 4
    chunk_size: int = 2000
    cache_enabled: bool = True
    
    def __post_init__(self):
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if self.chunk_size < 100:
            raise ValueError("chunk_size must be at least 100")


@dataclass
class ProcessingResult:
    """Result container with metrics"""
    anonymized_data: str
    entities_map: Dict[str, 'AnonymizedEntity']
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    cache_hits: int = 0
    total_entities: int = 0


def _import_facade():
    from facade import ArchitecturalPIIAnonymizer
    return ArchitecturalPIIAnonymizer

# Lazy import to avoid circular dependencies
ArchitecturalPIIAnonymizer = None

def get_anonymizer():
    global ArchitecturalPIIAnonymizer
    if ArchitecturalPIIAnonymizer is None:
        ArchitecturalPIIAnonymizer = _import_facade()
    return ArchitecturalPIIAnonymizer()