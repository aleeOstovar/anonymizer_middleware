# PII Anonymizer Module

A comprehensive PII detection and anonymization library with support for multiple languages, async processing, and architectural best practices following SOLID principles.

## Module Structure

```md
pii_anonymizer/
├── __init__.py              # Main module exports
├── core.py                  # Core types and data classes
├── interfaces.py            # Protocol interfaces (SOLID - Interface Segregation)
├── exceptions.py            # Exception hierarchy
├── cache.py                 # Caching strategies (Strategy pattern)
├── recognizers_base.py      # Abstract base recognizer
├── recognizers_english.py   # English PII recognizers
├── recognizers_german.py    # German PII recognizers  
├── recognizers_factory.py   # Factory for recognizers
├── fake_generator.py        # Fake data generation
├── analyzer.py              # Async PII analyzer engine
├── processing.py            # Main processing engine
├── deanonymization.py       # Deanonymization service
├── facade.py                # Main facade class
├── monitoring.py            # Performance monitoring
└── README.md                # This file
```

## Key Features

- **Multi-language support**: English and German with extensible architecture
- **Async processing**: Full async/await support with proper resource management
- **SOLID principles**: Clean architecture with proper separation of concerns
- **Comprehensive PII detection**: 30+ entity types including crypto wallets, medical licenses, German tax IDs, IBANs, etc.
- **Configurable anonymization**: Custom fake value generators and confidence thresholds
- **Performance monitoring**: Built-in metrics and caching
- **Deanonymization**: Restore original values using entity mappings

## Quick Start

```python
from pii_anonymizer import ArchitecturalPIIAnonymizer, Language

# Initialize the anonymizer
anonymizer = ArchitecturalPIIAnonymizer()

# Anonymize text (async)
result = await anonymizer.anonymize_text_async(
    text="My email is john.doe@company.com and phone is +49 123 456789",
    language=Language.GERMAN,
    confidence_threshold=0.7
)

print(result.anonymized_data)  # Anonymized text
print(result.entities_map)     # Mapping of original to fake values

# Synchronous version
result_sync = anonymizer.anonymize_text_sync(
    text="Same text here",
    language=Language.ENGLISH
)

# Deanonymize
original = anonymizer.deanonymize_text(
    result.anonymized_data, 
    result.entities_map
)
```

## Advanced Usage

### Custom Fake Generators

```python
def custom_email_generator(original_value: str) -> str:
    return f"masked_{len(original_value)}@example.org"

result = await anonymizer.anonymize_text_async(
    text="Contact: user@domain.com",
    custom_fake_generators={
        "EMAIL_ADDRESS": custom_email_generator
    }
)
```

### Analysis Only (No Anonymization)

```python
# Detect PII without anonymizing
entities = await anonymizer.analyze_only_async(
    text="John Smith lives at 123 Main St",
    entities_to_find=["PERSON", "LOCATION"],
    confidence_threshold=0.6
)

for entity in entities:
    print(f"Found {entity['entity_type']}: {entity['text']}")
```

### Batch Processing

```python
from pii_anonymizer import ProcessingConfig

config = ProcessingConfig(
    language=Language.GERMAN,
    confidence_threshold=0.8,
    cache_enabled=True,
    max_workers=8
)

async with anonymizer.batch_processing_context(config) as engine:
    texts = ["Text 1...", "Text 2...", "Text 3..."]
    results = []
    for text in texts:
        result = await engine.process_text_async(text)
        results.append(result)
```

### Performance Monitoring

```python
from pii_anonymizer import PerformanceMonitor

monitor = PerformanceMonitor()

# Process some texts...
result = anonymizer.anonymize_text_sync("Some PII text here")
monitor.record_processing(result)

# Get performance metrics
metrics = monitor.get_average_performance()
print(f"Average processing time: {metrics['avg_processing_time']:.3f}s")
print(f"Characters per second: {metrics['chars_per_second']:.0f}")
```

## Supported Languages

- **English**: Crypto wallets, medical licenses, professional licenses, NRP indicators
- **German**: Tax IDs, IBANs, phone numbers, addresses, health insurance, VAT IDs, and 20+ other German-specific entities

## Supported Entity Types

### Universal

- EMAIL_ADDRESS, PHONE_NUMBER, CREDIT_CARD, IP_ADDRESS, URL, PERSON, LOCATION, DATE_TIME, IBAN_CODE

### English-Specific  

- CRYPTO_WALLET, MEDICAL_LICENSE, PROFESSIONAL_LICENSE, NRP

### German-Specific

- DE_TAX_ID, DE_IBAN, DE_PHONE_NUMBER, DE_HEALTH_INSURANCE, DE_VAT_ID, DE_PASSPORT, DE_ID_CARD, DE_DRIVING_LICENSE, DE_STREET_ADDRESS, DE_POSTAL_CODE, and more

## Architecture Highlights

- **Interface Segregation**: Clean protocols for analyzers, recognizers, and generators
- **Dependency Inversion**: Abstract interfaces with concrete implementations  
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend with new languages and recognizers
- **Factory Pattern**: Centralized creation of language-specific recognizers
- **Strategy Pattern**: Pluggable caching strategies
- **Facade Pattern**: Simplified interface hiding system complexity

## Configuration Options

```python
from pii_anonymizer import ProcessingConfig, Language

config = ProcessingConfig(
    language=Language.GERMAN,
    entities_to_process=["PERSON", "EMAIL_ADDRESS", "DE_TAX_ID"],
    confidence_threshold=0.7,
    preserve_format=True,
    custom_fake_generators=custom_generators,
    max_workers=4,
    chunk_size=2000,
    cache_enabled=True
)
```

## Dependencies

- presidio-analyzer
- spacy (with language models)
- Standard library modules: asyncio, threading, hashlib, secrets

## Error Handling

The module provides a comprehensive exception hierarchy:

- `PIIAnonymizerError`: Base exception
- `ConfigurationError`: Configuration issues
- `ProcessingError`: Processing failures  
- `AnalysisError`: Analysis engine errors

All methods provide detailed error context and proper exception chaining
