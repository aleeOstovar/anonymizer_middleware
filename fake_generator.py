"""
Enhanced fake data generator for PII entities.
Generates realistic fake values for different types of PII data.
"""

import secrets
import hashlib
from typing import Dict, Callable, Optional

from core import Language


class FakeDataGenerator:
    """fake data generator with all original patterns"""
    
    def __init__(self, language: Language = Language.ENGLISH):
        self.language = language
        self._generators = self._create_generators()
    
    def generate_fake_value(
        self,
        entity_type: str,
        original_value: str,
        custom_generator: Optional[Callable] = None
    ) -> str:
        """Generate fake value - keeping original logic"""
        if custom_generator:
            return custom_generator(original_value)
        
        generator = self._generators.get(entity_type)
        if generator:
            return generator()
        else:
            return self._generate_default_value(entity_type, original_value)
    
    def generate_entity_id(self, entity_type: str, original_value: str) -> str:
        """Generate unique ID - keeping original logic"""
        hash_input = f"{entity_type}:{original_value}"
        entity_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        return f"{entity_type}_{entity_hash}"
    
    def _generate_default_value(self, entity_type: str, original_value: str) -> str:
        """Generate default value - keeping original logic"""
        return f"[{entity_type}_{secrets.token_hex(4)}]"
    
    def _create_generators(self) -> Dict[str, Callable]:
        """Create all original fake value generators"""
        generators = {
            # Keep ALL original universal generators
            "PERSON": lambda: f"Person_{secrets.token_hex(4)}",
            "EMAIL_ADDRESS": lambda: f"user{secrets.randbelow(9999)}@example.com",
            "PHONE_NUMBER": lambda: self._generate_phone_number(),
            "CREDIT_CARD": lambda: f"****-****-****-{secrets.randbelow(9000)+1000:04d}",
            "IP_ADDRESS": lambda: f"192.168.{secrets.randbelow(255)}.{secrets.randbelow(255)}",
            "LOCATION": lambda: f"City_{secrets.token_hex(3)}",
            "URL": lambda: f"https://example-{secrets.token_hex(4)}.com",
            "DATE_TIME": lambda: "YYYY-MM-DD HH:MM:SS",
            "IBAN_CODE": lambda: self._generate_iban(),
            "CRYPTO_WALLET": lambda: f"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa{secrets.token_hex(4)}",
            "MEDICAL_LICENSE": lambda: f"MD{secrets.randbelow(9999999):07d}",
            "NRP": lambda: f"GROUP_{secrets.token_hex(3)}",
            "PROFESSIONAL_LICENSE": lambda: f"LIC{secrets.randbelow(999999):06d}",
        }
        
        # Add German-specific generators if language is German
        if self.language == Language.GERMAN:
            generators.update(self._create_german_generators())
        
        return generators
    
    def _generate_phone_number(self) -> str:
        """Keep original phone number generation"""
        if self.language == Language.GERMAN:
            return f"+49{secrets.randbelow(9999):04d}{secrets.randbelow(99999999):08d}"
        else:
            return f"+1-555-{secrets.randbelow(900)+100:03d}-{secrets.randbelow(9000)+1000:04d}"
    
    def _generate_iban(self) -> str:
        """Keep original IBAN generation"""
        if self.language == Language.GERMAN:
            return f"DE{secrets.randbelow(90)+10:02d}{secrets.randbelow(9999999999999999):016d}"
        else:
            return f"GB{secrets.randbelow(90)+10:02d}ABCD{secrets.randbelow(999999999999):012d}"
    
    def _create_german_generators(self) -> Dict[str, Callable]:
        """Keep ALL original German generators"""
        return {
            "DE_TAX_ID": lambda: f"{secrets.randbelow(90000000000)+10000000000:011d}",
            "DE_PENSION_INSURANCE": lambda: f"{secrets.randbelow(90):02d}{secrets.randbelow(999999):06d}A{secrets.randbelow(999):03d}",
            "DE_HEALTH_INSURANCE": lambda: f"A{secrets.randbelow(9999999999):010d}",
            "DE_VAT_ID": lambda: f"DE{secrets.randbelow(999999999):09d}",
            "DE_IBAN": lambda: f"DE{secrets.randbelow(90)+10:02d}{secrets.randbelow(9999999999999999):016d}",
            "DE_PHONE_NUMBER": lambda: f"+49{secrets.randbelow(9999):04d}{secrets.randbelow(99999999):08d}",
            "DE_COMPANY_TAX": lambda: f"{secrets.randbelow(900)+100}/{secrets.randbelow(900)+100}/{secrets.randbelow(90000)+10000}",
            "DE_COMMERCIAL_REGISTER": lambda: f"HR{'BA'[secrets.randbelow(2)]}{secrets.randbelow(99999)+1000}",
            "BIC_SWIFT": lambda: f"DEUT{'DE'}2H{secrets.randbelow(999):03d}",
            "DE_STREET_ADDRESS": lambda: f"Musterstraße {secrets.randbelow(999)+1}",
            "DE_ID_CARD": lambda: f"{'ABCDEFGH'[secrets.randbelow(8)]}{secrets.randbelow(99999999):08d}",
            "DE_PASSPORT": lambda: f"{'ABCDEFGH'[secrets.randbelow(8)]}{'ABCDEFGH'[secrets.randbelow(8)]}{secrets.randbelow(9999999):07d}",
            "DE_DRIVING_LICENSE": lambda: f"DE{secrets.randbelow(99999999):08d}" if secrets.randbelow(2) else f"{secrets.randbelow(99999999999):011d}",
            "DE_RESIDENCE_PERMIT": lambda: f"{'ABCDEFGH'[secrets.randbelow(8)]}{secrets.randbelow(999999999):09d}{'ABCDEFGH'[secrets.randbelow(8)]}{secrets.randbelow(9)}",
            "DE_BANK_ACCOUNT": lambda: f"{secrets.randbelow(9999999999):010d}",
            "DE_SOCIAL_SECURITY": lambda: f"{secrets.randbelow(90):02d}{secrets.randbelow(999999):06d}A{secrets.randbelow(999):03d}",
            "DE_DATE_OF_BIRTH": lambda: f"{secrets.randbelow(28)+1:02d}.{secrets.randbelow(12)+1:02d}.{secrets.randbelow(50)+1950}",
            "DE_PERSON_NAME": lambda: f"Person_{secrets.token_hex(3)}",
            "DE_CREDIT_CARD": lambda: f"****-****-****-{secrets.randbelow(9000)+1000:04d}",
            "DE_CUSTOMER_ID": lambda: f"CUST-{secrets.randbelow(999999):06d}",
            "DE_EXPIRY_DATE": lambda: f"{secrets.randbelow(12)+1:02d}/{secrets.randbelow(10)+25:02d}",
            "DE_POSTAL_CODE": lambda: f"{secrets.randbelow(90000)+10000:05d}",
            "DE_STREET_NAME": lambda: f"Muster{['straße', 'gasse', 'weg', 'platz'][secrets.randbelow(4)]}"
        }