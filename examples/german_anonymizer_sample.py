"""
Sample German text anonymizer using in-memory caching.
This example demonstrates how to use the PII anonymizer with German text.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path to import modules directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import directly from the module files (fixed imports)
from facade import ArchitecturalPIIAnonymizer
from core import Language, ProcessingConfig
from cache import ThreadSafeLRUCache


async def anonymize_german_text():
    """
    Demonstrate German text anonymization with in-memory caching
    """
    # Sample German text with various PII types
    german_text = """
    Sehr geehrter Herr Schmidt,
    
    Vielen Dank für Ihre Anfrage. Wir haben Ihre Daten wie folgt gespeichert:
    
    Name: Thomas Schmidt
    Adresse: Musterstraße 123, 10115 Berlin
    Telefon: +49 30 12345678
    E-Mail: thomas.schmidt@example.de
    Steuer-ID: 12345678901
    IBAN: DE89 3704 0044 0532 0130 00
    Krankenversicherungsnummer: A123456789
    Personalausweisnummer: L01X00T47
    
    Bitte überweisen Sie den Betrag von 1.234,56 € bis zum 15.03.2023.
    
    Mit freundlichen Grüßen,
    Anna Müller
    Kundenservice
    """
    
    print("Original German text:")
    print("-" * 80)
    print(german_text)
    print("-" * 80)
    
    # Create anonymizer
    anonymizer = ArchitecturalPIIAnonymizer()
    
    # First anonymization (will be cached)
    print("\nPerforming first anonymization (no cache hit)...")
    start_time = asyncio.get_event_loop().time()
    
    result1 = await anonymizer.anonymize_text_async(
        text=german_text,
        language=Language.GERMAN,
        confidence_threshold=0.7,
        cache_enabled=True
    )
    
    end_time = asyncio.get_event_loop().time()
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # Display anonymized text
    print("\nAnonymized German text:")
    print("-" * 80)
    print(result1.anonymized_data)
    print("-" * 80)
    
    # Display detected entities
    print("\nDetected entities:")
    for entity_id, anonymized_entity in result1.entities_map.items():
        print(f"- {anonymized_entity.entity_type}: '{anonymized_entity.original_value}' -> '{anonymized_entity.fake_value}'")
    
    # Second anonymization (should hit cache)
    print("\nPerforming second anonymization (should hit cache)...")
    start_time = asyncio.get_event_loop().time()
    
    result2 = await anonymizer.anonymize_text_async(
        text=german_text,
        language=Language.GERMAN,
        confidence_threshold=0.7,
        cache_enabled=True
    )
    
    end_time = asyncio.get_event_loop().time()
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # Verify results are the same
    print(f"\nResults match: {result1.anonymized_data == result2.anonymized_data}")
    
    # Demonstrate deanonymization
    print("\nDeanonymized text (restoring original values):")
    print("-" * 80)
    deanonymized = anonymizer.deanonymize_text(
        result1.anonymized_data,
        result1.entities_map
    )
    print(deanonymized.anonymized_data)
    print("-" * 80)
    
    # Show German-specific entity types
    print("\nGerman-specific entity types supported:")
    german_entities = anonymizer.get_supported_entities(Language.GERMAN)
    for entity in german_entities:
        if entity.startswith("DE_"):
            print(f"- {entity}")


if __name__ == "__main__":
    asyncio.run(anonymize_german_text())