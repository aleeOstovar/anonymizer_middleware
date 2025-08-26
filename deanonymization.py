"""
Deanonymization service for restoring original PII values.
Implements Single Responsibility Principle for deanonymization operations.
"""

from typing import Dict, Union, Any

from core import AnonymizedEntity, ProcessingResult
from exceptions import ProcessingError


class DeanonymizationService:
    """Service for deanonymizing text"""
    
    @staticmethod
    def deanonymize_text(
        anonymized_text: str,
        entities_map: Dict[str, Union[AnonymizedEntity, Dict[str, Any]]]
    ) -> ProcessingResult:
        """Deanonymize text using entities map"""
        
        try:
            original_text = anonymized_text
            
            # Convert to consistent format
            processed_entities = []
            for entity_id, entity in entities_map.items():
                if isinstance(entity, dict):
                    processed_entities.append({
                        "fake_value": entity["fake_value"],
                        "original_value": entity["original_value"]
                    })
                else:
                    processed_entities.append({
                        "fake_value": entity.fake_value,
                        "original_value": entity.original_value
                    })
            
            # Sort by fake value length (longest first) to avoid partial replacements
            processed_entities.sort(key=lambda x: len(x["fake_value"]), reverse=True)
            
            # Replace fake values with originals
            for entity in processed_entities:
                if entity["fake_value"] in original_text:
                    original_text = original_text.replace(
                        entity["fake_value"], 
                        entity["original_value"]
                    )
            
            return ProcessingResult(
                anonymized_data=original_text,
                entities_map={},
                metadata={
                    "operation": "deanonymization",
                    "entities_processed": len(processed_entities)
                }
            )
            
        except Exception as e:
            raise ProcessingError(f"Deanonymization failed: {str(e)}")