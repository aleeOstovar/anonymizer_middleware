import secrets
import hashlib
from typing import Dict, Callable, Optional
from faker import Faker

from core import Language


class FakeDataGenerator:
    """Enhanced fake data generator with Faker library support"""
    
    def __init__(self, language: Language = Language.ENGLISH):
        self.language = language
        # Initialize Faker with appropriate locale
        self.fake = self._create_faker_instance()
        self._generators = self._create_generators()
    
    def _create_faker_instance(self) -> Faker:
        """Create Faker instance with appropriate locale"""
        if self.language == Language.GERMAN:
            return Faker('de_DE')
        else:
            return Faker('en_US')
    
    def generate_fake_value(
        self,
        entity_type: str,
        original_value: str,
        custom_generator: Optional[Callable] = None
    ) -> str:
        """Generate fake value using enhanced generators"""
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
        """Create enhanced fake value generators using Faker"""
        generators = {
            # Enhanced universal generators with Faker
            "PERSON": lambda: self.fake.name(),
            "FIRST_NAME": lambda: self.fake.first_name(),
            "LAST_NAME": lambda: self.fake.last_name(),
            "EMAIL_ADDRESS": lambda: self.fake.email(),
            "PHONE_NUMBER": lambda: self.fake.phone_number(),
            "CREDIT_CARD": lambda: self.fake.credit_card_number(),
            "IP_ADDRESS": lambda: self.fake.ipv4(),
            "IPV6_ADDRESS": lambda: self.fake.ipv6(),
            "LOCATION": lambda: self.fake.city(),
            "ADDRESS": lambda: self.fake.address().replace('\n', ', '),
            "STREET_ADDRESS": lambda: self.fake.street_address(),
            "CITY": lambda: self.fake.city(),
            "STATE": lambda: self.fake.state(),
            "COUNTRY": lambda: self.fake.country(),
            "POSTAL_CODE": lambda: self.fake.postcode(),
            "URL": lambda: self.fake.url(),
            "DOMAIN": lambda: self.fake.domain_name(),
            "DATE_TIME": lambda: self.fake.date_time().strftime("%Y-%m-%d %H:%M:%S"),
            "DATE": lambda: self.fake.date(),
            "TIME": lambda: self.fake.time(),
            "BIRTH_DATE": lambda: self.fake.date_of_birth().strftime("%Y-%m-%d"),
            "IBAN_CODE": lambda: self.fake.iban(),
            "CRYPTO_WALLET": lambda: f"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa{secrets.token_hex(4)}",
            "MEDICAL_LICENSE": lambda: f"MD{self.fake.random_number(digits=7, fix_len=True)}",
            "NRP": lambda: f"GROUP_{secrets.token_hex(3)}",
            "PROFESSIONAL_LICENSE": lambda: f"LIC{self.fake.random_number(digits=6, fix_len=True)}",
            "SSN": lambda: self.fake.ssn(),
            "COMPANY": lambda: self.fake.company(),
            "JOB_TITLE": lambda: self.fake.job(),
            "USERNAME": lambda: self.fake.user_name(),
            "PASSWORD": lambda: self.fake.password(),
            "UUID": lambda: str(self.fake.uuid4()),
            "MAC_ADDRESS": lambda: self.fake.mac_address(),
            "USER_AGENT": lambda: self.fake.user_agent(),
            "BANK_ACCOUNT": lambda: self.fake.bban(),
            "SWIFT_CODE": lambda: self.fake.swift(),
            "CURRENCY_CODE": lambda: self.fake.currency_code(),
            "LICENSE_PLATE": lambda: self.fake.license_plate(),
            "VIN": lambda: self.fake.vin() if hasattr(self.fake, 'vin') else f"VIN{secrets.token_hex(8).upper()}",
        }
        
        # Add language-specific generators
        if self.language == Language.GERMAN:
            generators.update(self._create_german_generators())
        else:
            generators.update(self._create_english_generators())
        
        return generators
    
    def _create_english_generators(self) -> Dict[str, Callable]:
        """Create English-specific generators"""
        return {
            "US_SSN": lambda: self.fake.ssn(),
            "US_PHONE": lambda: self.fake.phone_number(),
            "US_STATE": lambda: self.fake.state(),
            "US_ZIP_CODE": lambda: self.fake.zipcode(),
            "UK_POSTCODE": lambda: self.fake.postcode() if 'GB' in str(self.fake) else f"{self.fake.lexify('??')} {self.fake.numerify('#??')}",
            "DRIVER_LICENSE": lambda: f"D{self.fake.random_number(digits=8)}",
        }
    
    def _create_german_generators(self) -> Dict[str, Callable]:
        """Create German-specific generators with enhanced Faker support"""
        return {
            # Keep original custom German generators for specific formats
            "DE_TAX_ID": lambda: f"{self.fake.random_number(digits=11)}",
            "DE_PENSION_INSURANCE": lambda: f"{self.fake.random_number(digits=2, fix_len=True)}{self.fake.random_number(digits=6, fix_len=True)}A{self.fake.random_number(digits=3, fix_len=True)}",
            "DE_HEALTH_INSURANCE": lambda: f"A{self.fake.random_number(digits=10, fix_len=True)}",
            "DE_VAT_ID": lambda: f"DE{self.fake.random_number(digits=9, fix_len=True)}",
            "DE_IBAN": lambda: self.fake.iban(),
            "DE_PHONE_NUMBER": lambda: self.fake.phone_number(),
            "DE_COMPANY_TAX": lambda: f"{self.fake.random_number(digits=3)}/{self.fake.random_number(digits=3)}/{self.fake.random_number(digits=5)}",
            "DE_COMMERCIAL_REGISTER": lambda: f"HR{self.fake.random_element(['A', 'B'])}{self.fake.random_number(digits=5)}",
            "BIC_SWIFT": lambda: self.fake.swift(),
            "DE_STREET_ADDRESS": lambda: self.fake.street_address(),
            "DE_ID_CARD": lambda: f"{self.fake.random_letter().upper()}{self.fake.random_number(digits=8, fix_len=True)}",
            "DE_PASSPORT": lambda: f"{self.fake.random_letter().upper()}{self.fake.random_letter().upper()}{self.fake.random_number(digits=7, fix_len=True)}",
            "DE_DRIVING_LICENSE": lambda: f"DE{self.fake.random_number(digits=8, fix_len=True)}" if self.fake.boolean() else f"{self.fake.random_number(digits=11, fix_len=True)}",
            "DE_RESIDENCE_PERMIT": lambda: f"{self.fake.random_letter().upper()}{self.fake.random_number(digits=9, fix_len=True)}{self.fake.random_letter().upper()}{self.fake.random_number(digits=1)}",
            "DE_BANK_ACCOUNT": lambda: f"{self.fake.random_number(digits=10, fix_len=True)}",
            "DE_SOCIAL_SECURITY": lambda: f"{self.fake.random_number(digits=2, fix_len=True)}{self.fake.random_number(digits=6, fix_len=True)}A{self.fake.random_number(digits=3, fix_len=True)}",
            "DE_DATE_OF_BIRTH": lambda: self.fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"),
            "DE_PERSON_NAME": lambda: self.fake.name(),
            "DE_FIRST_NAME": lambda: self.fake.first_name(),
            "DE_LAST_NAME": lambda: self.fake.last_name(),
            "DE_CREDIT_CARD": lambda: self.fake.credit_card_number(),
            "DE_CUSTOMER_ID": lambda: f"CUST-{self.fake.random_number(digits=6, fix_len=True)}",
            "DE_EXPIRY_DATE": lambda: f"{self.fake.random_number(digits=2, fix_len=True)}/{self.fake.random_number(digits=2, fix_len=True)}",
            "DE_POSTAL_CODE": lambda: self.fake.postcode(),
            "DE_STREET_NAME": lambda: f"{self.fake.word().capitalize()}{self.fake.random_element(['straße', 'gasse', 'weg', 'platz'])}",
            "DE_CITY": lambda: self.fake.city(),
            "DE_STATE": lambda: self.fake.state(),
            "DE_COMPANY": lambda: self.fake.company(),
            "DE_EMAIL": lambda: self.fake.email(),
            "DE_USERNAME": lambda: self.fake.user_name(),
            "DE_URL": lambda: self.fake.url(),
            "DE_DOMAIN": lambda: self.fake.domain_name(),
        }
    
    def get_available_entity_types(self) -> list:
        """Get list of all available entity types"""
        return list(self._generators.keys())
    
    def generate_consistent_fake_value(self, entity_type: str, original_value: str) -> str:
        """Generate consistent fake value for the same original value"""
        # Use original value as seed for consistent generation
        self.fake.seed_instance(hash(original_value))
        fake_value = self.generate_fake_value(entity_type, original_value)
        # Reset seed
        self.fake.seed_instance(None)
        return fake_value
    
    def bulk_generate(self, entity_mappings: Dict[str, str], consistent: bool = True) -> Dict[str, str]:
        """Generate fake values for multiple entities at once"""
        results = {}
        for entity_type, original_value in entity_mappings.items():
            if consistent:
                results[original_value] = self.generate_consistent_fake_value(entity_type, original_value)
            else:
                results[original_value] = self.generate_fake_value(entity_type, original_value)
        return results