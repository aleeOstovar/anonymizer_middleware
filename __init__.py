import env_loader

from core import (
    Language,
    EntityMatch,
    AnonymizedEntity,
    ProcessingConfig,
    ProcessingResult,
)

from facade import ArchitecturalPIIAnonymizer

from exceptions import (
    PIIAnonymizerError,
    ConfigurationError,
    ProcessingError,
    AnalysisError
)

from interfaces import (
    IAnalyzer,
    IRecognizer,
    IFakeDataGenerator,
    ICacheStrategy
)

from monitoring import PerformanceMonitor

__version__ = "1.0.0"
__author__ = "PII Anonymizer Team"

# Main API exports
__all__ = [
    # Core classes
    "ArchitecturalPIIAnonymizer",
    "Language",
    "EntityMatch", 
    "AnonymizedEntity",
    "ProcessingConfig",
    "ProcessingResult",
    
    # Exceptions
    "PIIAnonymizerError",
    "ConfigurationError", 
    "ProcessingError",
    "AnalysisError",
    
    # Interfaces
    "IAnalyzer",
    "IRecognizer", 
    "IFakeDataGenerator",
    "ICacheStrategy",
    
    # Utilities
    "PerformanceMonitor"
]