"""
English language recognizers with enhanced patterns for specific entities.
Extends BaseRecognizer for English-specific PII detection.
"""

from typing import List
from presidio_analyzer import PatternRecognizer, Pattern

from recognizers_base import BaseRecognizer


class EnglishRecognizers(BaseRecognizer):
    """English recognizers with all original patterns"""
    
    def _create_recognizers(self) -> List[PatternRecognizer]:
        """Create all English recognizers with full regex patterns"""
        return [
            self._create_crypto_wallet_recognizer(),
            self._create_medical_license_recognizer(),
            self._create_enhanced_license_recognizer(),
            self._create_nrp_recognizer(),
        ]
    
    def _get_entity_types(self) -> List[str]:
        return ["CRYPTO_WALLET", "MEDICAL_LICENSE", "PROFESSIONAL_LICENSE", "NRP"]
    
    def _create_crypto_wallet_recognizer(self) -> PatternRecognizer:
        """Cryptocurrency wallet addresses - keeping original patterns"""
        patterns = [
            Pattern(
                name="bitcoin_address",
                regex=r"\b(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b",
                score=0.8
            ),
            Pattern(
                name="ethereum_address",
                regex=r"\b0x[a-fA-F0-9]{40}\b",
                score=0.8
            )
        ]
        return PatternRecognizer(
            supported_entity="CRYPTO_WALLET",
            patterns=patterns,
            supported_language="en"
        )
    
    def _create_medical_license_recognizer(self) -> PatternRecognizer:
        """Medical license numbers - keeping original patterns"""
        patterns = [
            Pattern(
                name="medical_license",
                regex=r"\b(?:MD|DO|NP|PA|RN|LPN|DDS|DMD|PharmD)[\s-]?\d{6,10}\b",
                score=0.7
            ),
            Pattern(
                name="dea_number",
                regex=r"\b[A-Z]{2}\d{7}\b",
                score=0.8
            )
        ]
        return PatternRecognizer(
            supported_entity="MEDICAL_LICENSE",
            patterns=patterns,
            supported_language="en"
        )
    
    def _create_enhanced_license_recognizer(self) -> PatternRecognizer:
        """Various license types - keeping original patterns"""
        patterns = [
            Pattern(
                name="generic_license",
                regex=r"\b(?:LIC|LICENSE|PERMIT)[\s-]?\d{6,12}\b",
                score=0.6
            ),
            Pattern(
                name="professional_license",
                regex=r"\b(?:CPA|PE|ESQ|JD|MD|PhD|DDS)[\s-]?\d{4,10}\b",
                score=0.7
            )
        ]
        return PatternRecognizer(
            supported_entity="PROFESSIONAL_LICENSE",
            patterns=patterns,
            supported_language="en"
        )
    
    def _create_nrp_recognizer(self) -> PatternRecognizer:
        """Nationality, Religious, Political group indicators - keeping original patterns"""
        patterns = [
            Pattern(
                name="nationality_indicator",
                regex=r"\b(?:nationality|citizen(?:ship)?|national(?:ity)?)[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
                score=0.6
            ),
            Pattern(
                name="religion_indicator",
                regex=r"\b(?:religion|religious|faith|belief)[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
                score=0.6
            ),
            Pattern(
                name="political_indicator",
                regex=r"\b(?:political|party|affiliation)[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
                score=0.6
            )
        ]
        return PatternRecognizer(
            supported_entity="NRP",
            patterns=patterns,
            supported_language="de"
        )