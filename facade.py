"""
Main facade class implementing the Facade pattern.
Provides a simplified interface to the entire PII anonymization system.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Callable, Union, Any

from core import Language, ProcessingConfig, ProcessingResult, AnonymizedEntity
from processing import AsyncPIIProcessingEngine
from deanonymization import DeanonymizationService
from analyzer import AsyncPIIAnalyzerEngine
from cache import ThreadSafeLRUCache, NoCacheStrategy
from recognizers_factory import RecognizerFactory


class ArchitecturalPIIAnonymizer:
    """
    Main PII Anonymizer implementing architectural best practices:
    - SOLID principles
    - Async/await patterns
    - Factory and Strategy patterns
    - Proper dependency injection
    - Comprehensive error handling
    """
    
    def __init__(self):
        self._deanonymization_service = DeanonymizationService()
    
    async def anonymize_text_async(
        self,
        text: str,
        language: Language = Language.ENGLISH,
        entities_to_anonymize: Optional[List[str]] = None,
        confidence_threshold: float = 0.5,
        max_workers: int = 4,
        chunk_size: int = 2000,
        cache_enabled: bool = True,
        custom_fake_generators: Optional[Dict[str, Callable]] = None
    ) -> ProcessingResult:
        """
        Async anonymization with all architectural improvements
        
        Args:
            text: Text to anonymize
            language: Language for processing (keeps large spaCy models)
            entities_to_anonymize: Specific entities to target (None for all)
            confidence_threshold: Minimum confidence threshold
            max_workers: Number of async workers
            chunk_size: Size for text chunking
            cache_enabled: Whether to use caching
            custom_fake_generators: Custom fake value generators
        
        Returns:
            ProcessingResult with performance metrics
        """
        
        config = ProcessingConfig(
            language=language,
            entities_to_process=entities_to_anonymize,
            confidence_threshold=confidence_threshold,
            max_workers=max_workers,
            chunk_size=chunk_size,
            cache_enabled=cache_enabled,
            custom_fake_generators=custom_fake_generators
        )
        
        engine = AsyncPIIProcessingEngine(config)
        return await engine.process_text_async(text)
    
    def anonymize_text_sync(
        self,
        text: str,
        language: Language = Language.ENGLISH,
        **kwargs
    ) -> ProcessingResult:
        """Synchronous wrapper for async anonymization"""
        return asyncio.run(self.anonymize_text_async(text, language, **kwargs))
    
    def deanonymize_text(
        self,
        anonymized_text: str,
        entities_map: Dict[str, Union[AnonymizedEntity, Dict[str, Any]]]
    ) -> ProcessingResult:
        """Deanonymize text using entities map"""
        return self._deanonymization_service.deanonymize_text(anonymized_text, entities_map)
    
    async def analyze_only_async(
        self,
        text: str,
        language: Language = Language.ENGLISH,
        entities_to_find: Optional[List[str]] = None,
        confidence_threshold: float = 0.5,
        cache_enabled: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Analyze text without anonymization (async)
        """
        
        config = ProcessingConfig(
            language=language,
            entities_to_process=entities_to_find,
            confidence_threshold=confidence_threshold,
            cache_enabled=cache_enabled
        )
        
        entities_to_analyze = (entities_to_find or 
                             RecognizerFactory.get_all_supported_entities(language))
        
        cache_strategy = ThreadSafeLRUCache() if cache_enabled else NoCacheStrategy()
        
        async with AsyncPIIAnalyzerEngine(cache_strategy) as analyzer:
            entities = await analyzer.analyze_async(text, language, entities_to_analyze)
        
        # Filter by confidence
        filtered_entities = [e for e in entities if e.confidence >= confidence_threshold]
        return [entity.to_dict() for entity in filtered_entities]
    
    def analyze_only_sync(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Synchronous wrapper for analysis"""
        return asyncio.run(self.analyze_only_async(text, **kwargs))
    
    def get_supported_entities(self, language: Language) -> List[str]:
        """Get all supported entities for a language"""
        return RecognizerFactory.get_all_supported_entities(language)
    
    def get_supported_languages(self) -> List[str]:
        """Get all supported languages"""
        return [lang.value for lang in Language]
    
    @asynccontextmanager
    async def batch_processing_context(self, config: ProcessingConfig):
        """Context manager for batch processing optimization"""
        engine = AsyncPIIProcessingEngine(config)
        try:
            yield engine
        finally:
            # Cleanup resources
            pass