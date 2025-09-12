# PII Anonymizer

A robust, enterprise-grade Python library for detecting and anonymizing Personally Identifiable Information (PII) in text data. Built with architectural best practices including async/await patterns, SOLID principles, and comprehensive caching strategies.

## Features

- **Multi-language Support**: English and German text processing with language-specific recognizers
- **Async/Await Architecture**: High-performance asynchronous processing with proper resource management
- **Advanced PII Detection**: Leverages Microsoft Presidio for accurate entity recognition
- **Flexible Anonymization**: Configurable fake data generation using Faker library
- **Caching Strategies**: In-memory LRU cache and Redis cache support for improved performance
- **Deanonymization**: Reversible anonymization with entity mapping
- **Comprehensive Testing**: Full test coverage with async testing patterns
- **Type Safety**: Complete type hints and validation

## Supported PII Entities

### Universal Entities

- Credit Card Numbers
- Email Addresses
- Phone Numbers
- IP Addresses
- URLs
- Dates and Times
- Person Names
- Locations

### German-Specific Entities

- German Tax ID (Steuer-ID)
- German IBAN
- German Insurance Numbers
- German ID Card Numbers

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install spaCy language models
python -m spacy download en_core_web_lg
python -m spacy download de_core_news_lg
```

## Quick Start

### Basic Usage

```python
import asyncio
from facade import ArchitecturalPIIAnonymizer
from core import Language

async def main():
    anonymizer = ArchitecturalPIIAnonymizer()

    text = "John Smith's email is john.smith@example.com and his phone is +1-555-123-4567"

    result = await anonymizer.anonymize_text_async(
        text=text,
        language=Language.ENGLISH,
        confidence_threshold=0.7
    )

    print("Anonymized:", result.anonymized_data)
    print("Entities found:", len(result.entities_map))

asyncio.run(main())
```

### Synchronous Usage

```python
from facade import ArchitecturalPIIAnonymizer
from core import Language

anonymizer = ArchitecturalPIIAnonymizer()

result = anonymizer.anonymize_text_sync(
    text="Contact Jane Doe at jane.doe@company.com",
    language=Language.ENGLISH
)

print("Anonymized:", result.anonymized_data)
```

### German Text Processing

```python
import asyncio
from facade import ArchitecturalPIIAnonymizer
from core import Language

async def anonymize_german():
    anonymizer = ArchitecturalPIIAnonymizer()

    german_text = """
    Name: Thomas Schmidt
    E-Mail: thomas.schmidt@example.de
    IBAN: DE89 3704 0044 0532 0130 00
    """

    result = await anonymizer.anonymize_text_async(
        text=german_text,
        language=Language.GERMAN,
        confidence_threshold=0.7
    )

    print("Anonymized German text:", result.anonymized_data)

asyncio.run(anonymize_german())
```

## Advanced Configuration

### Custom Processing Configuration

```python
from core import ProcessingConfig, Language

config = ProcessingConfig(
    language=Language.ENGLISH,
    entities_to_process=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
    confidence_threshold=0.8,
    preserve_format=True,
    max_workers=8,
    chunk_size=5000,
    cache_enabled=True
)
```

### Custom Fake Data Generators

```python
def custom_email_generator(original_value):
    return f"user{hash(original_value) % 1000}@company.com"

custom_generators = {
    "EMAIL_ADDRESS": custom_email_generator
}

result = await anonymizer.anonymize_text_async(
    text=text,
    custom_fake_generators=custom_generators
)
```

### Batch Processing

```python
async def batch_process():
    anonymizer = ArchitecturalPIIAnonymizer()
    config = ProcessingConfig(language=Language.ENGLISH)

    async with anonymizer.batch_processing_context(config) as engine:
        for text in text_batch:
            result = await engine.process_text_async(text)
            # Process result
```

## Deanonymization

```python
# Anonymize text
result = anonymizer.anonymize_text_sync(text="John Smith")

# Later, restore original values
restored = anonymizer.deanonymize_text(
    anonymized_text=result.anonymized_data,
    entities_map=result.entities_map
)

print("Restored:", restored.anonymized_data)  # "John Smith"
```

## Analysis Only (No Anonymization)

```python
# Just detect PII without anonymizing
entities = await anonymizer.analyze_only_async(
    text="Contact John at john@example.com",
    language=Language.ENGLISH,
    confidence_threshold=0.7
)

for entity in entities:
    print(f"Found {entity['entity_type']}: {entity['text']}")
```

## Caching

### In-Memory Cache (Default)

```python
# Automatic LRU cache with 1000 item limit
result = await anonymizer.anonymize_text_async(text, cache_enabled=True)
```

### Redis Cache

```python
# Configure Redis in environment variables
# REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
result = await anonymizer.anonymize_text_async(text, cache_enabled=True)
```

## Environment Configuration

Create a `.env` file for default settings:

```env
DEFAULT_LANGUAGE=en
DEFAULT_CONFIDENCE_THRESHOLD=0.5
PRESERVE_FORMAT=true
DEFAULT_MAX_WORKERS=4
DEFAULT_CHUNK_SIZE=2000
CACHE_ENABLED=true

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

## Architecture

The library follows SOLID principles and implements several design patterns:

- **Facade Pattern**: `ArchitecturalPIIAnonymizer` provides a simplified interface
- **Factory Pattern**: `RecognizerFactory` creates language-specific recognizers
- **Strategy Pattern**: Pluggable cache strategies (LRU, Redis, No-cache)
- **Async Context Managers**: Proper resource management for async operations
- **Dependency Injection**: Configurable components for testing and flexibility

## Performance Features

- **Asynchronous Processing**: Non-blocking I/O operations
- **Chunked Processing**: Large texts split into manageable chunks
- **Thread Pool Execution**: CPU-intensive tasks run in thread pools
- **Intelligent Caching**: Reduces redundant analysis operations
- **Memory Management**: Proper cleanup and resource management

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m unittest tests.test_facade

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Error Handling

The library provides comprehensive error handling:

```python
from exceptions import PIIAnonymizerError, ConfigurationError, ProcessingError

try:
    result = await anonymizer.anonymize_text_async(text)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ProcessingError as e:
    print(f"Processing error: {e}")
except PIIAnonymizerError as e:
    print(f"General error: {e}")
```

## API Reference

### Main Classes

- `ArchitecturalPIIAnonymizer`: Main facade class
- `ProcessingConfig`: Configuration for processing
- `ProcessingResult`: Result container with metrics
- `Language`: Supported languages enum
- `EntityMatch`: Detected entity representation
- `AnonymizedEntity`: Anonymized entity with metadata

### Key Methods

- `anonymize_text_async()`: Async text anonymization
- `anonymize_text_sync()`: Sync text anonymization
- `analyze_only_async()`: PII detection without anonymization
- `deanonymize_text()`: Restore original values
- `get_supported_entities()`: List supported entity types
- `get_supported_languages()`: List supported languages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

- `presidio-analyzer>=2.2.0`: Core PII detection engine
- `spacy>=3.5.0`: Natural language processing
- `faker>=18.0.0`: Fake data generation
- `redis>=4.5.0`: Redis caching support
- `asyncio>=3.4.3`: Async support
- `typing-extensions>=4.5.0`: Enhanced type hints

## Version

Current version: 1.0.0
