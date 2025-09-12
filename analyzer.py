"""
Async analyzer engine for PII detection.
Implements async patterns with proper resource management and caching.
"""

import asyncio
import threading
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from core import Language, EntityMatch
from exceptions import AnalysisError
from interfaces import ICacheStrategy
from recognizers_factory import RecognizerFactory


class AsyncPIIAnalyzerEngine:
    """Async analyzer engine with proper resource management"""
    
    def __init__(self, cache_strategy: Optional[ICacheStrategy] = None):
        from cache import ThreadSafeLRUCache
        from redis_cache import RedisCache
        
        self._analyzers: Dict[str, AnalyzerEngine] = {}
        self._analyzer_lock = threading.RLock()
        self._cache = cache_strategy if cache_strategy is not None else ThreadSafeLRUCache(maxsize=1000)
        self._executor: Optional[ThreadPoolExecutor] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self._executor = ThreadPoolExecutor(max_workers=4)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None
    
    def _get_cache_key(self, text: str, language: Language, entities: List[str]) -> str:
        """Generate cache key"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        entities_str = ",".join(sorted(entities))
        return f"{text_hash}_{language.value}_{entities_str}"
    
    def _get_or_create_analyzer(self, language: Language) -> AnalyzerEngine:
        """Thread-safe lazy initialization of analyzers"""
        lang_code = language.value
        if lang_code not in self._analyzers:
            with self._analyzer_lock:
                if lang_code not in self._analyzers:
                    self._analyzers[lang_code] = self._create_analyzer(language)
        return self._analyzers[lang_code]
    
    def _create_analyzer(self, language: Language) -> AnalyzerEngine:
        """Create analyzer with large spaCy models and all recognizers"""
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(languages=[language.value])
        
        # Add custom recognizers
        recognizer = RecognizerFactory.create_recognizer(language)
        for custom_recognizer in recognizer.get_recognizers():
            registry.add_recognizer(custom_recognizer)
        
        # Use large spaCy models as requested
        model_name = f"{language.value}_core_news_lg"  # Keep large models
        nlp_config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": language.value, "model_name": model_name}],
        }
        
        try:
            provider = NlpEngineProvider(nlp_configuration=nlp_config)
            nlp_engine = provider.create_engine()
        except Exception as e:
            raise AnalysisError(f"Failed to create NLP engine for {language.value}: {str(e)}")
        
        return AnalyzerEngine(
            registry=registry,
            nlp_engine=nlp_engine,
            default_score_threshold=0.1  # Low threshold, we filter later
        )
    
    async def analyze_async(
        self,
        text: str,
        language: Language,
        entities: List[str]
    ) -> List[EntityMatch]:
        """Async analysis with caching"""
        
        # Check cache first
        cache_key = self._get_cache_key(text, language, entities)
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Perform analysis in thread pool
        if not self._executor:
            from .exceptions import ProcessingError
            raise ProcessingError("Analyzer not properly initialized. Use async context manager.")
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self._executor,
            self._analyze_sync_internal,
            text, language, entities
        )
        
        # Cache the result
        self._cache.set(cache_key, result)
        return result
    
    def _analyze_sync_internal(
        self,
        text: str,
        language: Language,
        entities: List[str]
    ) -> List[EntityMatch]:
        """Internal synchronous analysis"""
        try:
            analyzer = self._get_or_create_analyzer(language)
            results = analyzer.analyze(
                text=text,
                entities=entities,
                language=language.value
            )
            
            return [
                EntityMatch(
                    entity_type=result.entity_type,
                    start=result.start,
                    end=result.end,
                    text=text[result.start:result.end],
                    confidence=result.score
                )
                for result in results
            ]
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {str(e)}")