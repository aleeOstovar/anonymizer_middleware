from typing import Optional, Dict, Any
class PIIAnonymizerError(Exception):
    """Base exception with error context"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(PIIAnonymizerError):
    """Configuration-related errors"""
    pass


class ProcessingError(PIIAnonymizerError):
    """Processing-related errors"""
    pass


class AnalysisError(PIIAnonymizerError):
    """Analysis-related errors"""
    pass