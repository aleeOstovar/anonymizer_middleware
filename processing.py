"""
Main processing engine implementing the Facade pattern.
Orchestrates the entire PII anonymization process.
"""

import time
from typing import Dict, List, Tuple

from core import Language, ProcessingConfig, ProcessingResult, EntityMatch, AnonymizedEntity
from exceptions import ProcessingError
from cache import ThreadSafeLRUCache, NoCacheStrategy
from analyzer import AsyncPIIAnalyzerEngine
from fake_generator import FakeDataGenerator
from recognizers_factory import RecognizerFactory


class AsyncPIIProcessingEngine:
    """Main processing engine implementing Facade pattern"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self._cache_strategy = ThreadSafeLRUCache() if config.cache_enabled else NoCacheStrategy()
        self._fake_generators: Dict[Language, FakeDataGenerator] = {}
    
    def _get_fake_generator(self, language: Language) -> FakeDataGenerator:
        """Get or create fake data generator for language"""
        if language not in self._fake_generators:
            self._fake_generators[language] = FakeDataGenerator(language)
        return self._fake_generators[language]
    
    async def process_text_async(self, text: str) -> ProcessingResult:
        """Main async processing method"""
        start_time = time.time()
        
        try:
            # Get entities to process
            entities_to_analyze = self._get_entities_to_analyze()
            
            # Analyze text asynchronously
            async with AsyncPIIAnalyzerEngine(self._cache_strategy) as analyzer:
                detected_entities = await analyzer.analyze_async(
                    text=text,
                    language=self.config.language,
                    entities=entities_to_analyze
                )
            
            # Filter and process entities
            filtered_entities = self._filter_entities(detected_entities)
            merged_entities = self._merge_overlapping_entities(filtered_entities)
            
            # Anonymize
            anonymized_text, entities_map = self._anonymize_entities(text, merged_entities)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                anonymized_data=anonymized_text,
                entities_map=entities_map,
                processing_time=processing_time,
                total_entities=len(merged_entities),
                metadata={
                    "language": self.config.language.value,
                    "confidence_threshold": self.config.confidence_threshold,
                    "entities_processed": len(merged_entities),
                    "text_length": len(text)
                }
            )
            
        except Exception as e:
            raise ProcessingError(f"Text processing failed: {str(e)}")
    
    def _get_entities_to_analyze(self) -> List[str]:
        """Get entities to analyze based on configuration"""
        if self.config.entities_to_process:
            return self.config.entities_to_process
        return RecognizerFactory.get_all_supported_entities(self.config.language)
    
    def _filter_entities(self, entities: List[EntityMatch]) -> List[EntityMatch]:
        """Filter entities by confidence threshold"""
        return [e for e in entities if e.confidence >= self.config.confidence_threshold]
    
    def _merge_overlapping_entities(self, entities: List[EntityMatch]) -> List[EntityMatch]:
        """Merge overlapping entities keeping higher confidence ones"""
        if not entities:
            return []
        
        sorted_entities = sorted(entities, key=lambda x: x.start)
        merged = [sorted_entities[0]]
        
        for current in sorted_entities[1:]:
            last = merged[-1]
            if current.start < last.end:
                # Overlap detected - keep higher confidence
                if current.confidence > last.confidence:
                    merged[-1] = current
            else:
                merged.append(current)
        
        return merged
    
    def _anonymize_entities(
        self, 
        text: str, 
        entities: List[EntityMatch]
    ) -> Tuple[str, Dict[str, AnonymizedEntity]]:
        """Anonymize detected entities"""
        fake_generator = self._get_fake_generator(self.config.language)
        entities_map = {}
        anonymized_text = text
        
        # Sort by start position in reverse order for safe replacement
        sorted_entities = sorted(entities, key=lambda x: x.start, reverse=True)
        
        for entity in sorted_entities:
            entity_id = fake_generator.generate_entity_id(entity.entity_type, entity.text)
            
            # Get custom generator if provided
            custom_generator = None
            if (self.config.custom_fake_generators and 
                entity.entity_type in self.config.custom_fake_generators):
                custom_generator = self.config.custom_fake_generators[entity.entity_type]
            
            fake_value = fake_generator.generate_fake_value(
                entity.entity_type, entity.text, custom_generator
            )
            
            # Create anonymized entity
            anonymized_entity = AnonymizedEntity(
                entity_id=entity_id,
                original_value=entity.text,
                entity_type=entity.entity_type,
                fake_value=fake_value,
                confidence=entity.confidence
            )
            
            entities_map[entity_id] = anonymized_entity
            
            # Replace in text
            anonymized_text = (
                anonymized_text[:entity.start] +
                fake_value +
                anonymized_text[entity.end:]
            )
        
        return anonymized_text, entities_map