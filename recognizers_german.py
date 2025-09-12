"""
Enhanced German language recognizers with improved patterns for higher F1 score.
Focus on flexibility, context awareness, and comprehensive coverage.
"""

from typing import List
from presidio_analyzer import PatternRecognizer, Pattern

from recognizers_base import BaseRecognizer


class GermanRecognizers(BaseRecognizer):
    """Enhanced German recognizers with improved patterns for higher F1 score"""
    
    def _create_recognizers(self) -> List[PatternRecognizer]:
        """Create all German recognizers with enhanced patterns"""
        return [
            self._create_tax_id_recognizer(),
            self._create_pension_insurance_recognizer(),
            self._create_health_insurance_recognizer(),
            self._create_company_tax_recognizer(),
            self._create_vat_id_recognizer(),
            self._create_commercial_register_recognizer(),
            self._create_german_iban_recognizer(),
            self._create_bic_swift_recognizer(),
            self._create_german_phone_recognizer(),
            self._create_german_address_recognizer(),
            self._create_german_id_card_recognizer(),
            self._create_german_passport_recognizer(),
            self._create_german_driving_license_recognizer(),
            self._create_residence_permit_recognizer(),
            self._create_german_bank_account_recognizer(),
            self._create_german_social_security_recognizer(),
            self._create_german_date_of_birth_recognizer(),
            self._create_german_name_recognizer(),
            self._create_german_credit_card_recognizer(),
            self._create_german_customer_id_recognizer(),
            self._create_german_expiry_date_recognizer(),
            self._create_german_postal_code_recognizer(),
            self._create_german_street_name_recognizer(),
        ]
    
    def _get_entity_types(self) -> List[str]:
        return [
            "DE_TAX_ID", "DE_PENSION_INSURANCE", "DE_HEALTH_INSURANCE",
            "DE_COMPANY_TAX", "DE_VAT_ID", "DE_COMMERCIAL_REGISTER",
            "DE_IBAN", "BIC_SWIFT", "DE_PHONE_NUMBER", "DE_STREET_ADDRESS",
            "DE_ID_CARD", "DE_PASSPORT", "DE_DRIVING_LICENSE",
            "DE_RESIDENCE_PERMIT", "DE_BANK_ACCOUNT", "DE_SOCIAL_SECURITY",
            "DE_DATE_OF_BIRTH", "DE_PERSON_NAME", "DE_CREDIT_CARD",
            "DE_CUSTOMER_ID", "DE_EXPIRY_DATE", "DE_POSTAL_CODE", "DE_STREET_NAME"
        ]
    
    def _create_tax_id_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Enhanced with more flexible spacing and separators
            Pattern(
                name="german_tax_id_flexible",
                regex=r"\b\d{2}[\s\-\.]?\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{3}\b",
                score=0.9
            ),
            Pattern(
                name="german_tax_id_continuous",
                regex=r"\b\d{11}\b",
                score=0.85
            ),
            # Context-aware patterns
            Pattern(
                name="german_tax_id_context",
                regex=r"(?i)\b(?:steuer[^\w]*?id|steuer[^\w]*?nummer|steuernummer|identifikationsnummer|steuerliche\s+identifikationsnummer)[\s:]*(\d{2}[\s\-\.]?\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{3})\b",
                score=0.98
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_TAX_ID",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_pension_insurance_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_pension_insurance_flexible",
                regex=r"\b\d{2}[\s\-]?\d{6}[\s\-]?[A-Z][\s\-]?\d{3}\b",
                score=0.85
            ),
            Pattern(
                name="german_pension_insurance_context",
                regex=r"(?i)\b(?:renten[^\w]*?versicherungs[^\w]*?nummer|rvnr|sozialversicherungsnummer)[\s:]*(\d{2}[\s\-]?\d{6}[\s\-]?[A-Z][\s\-]?\d{3})\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_PENSION_INSURANCE",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_health_insurance_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_health_insurance_standard",
                regex=r"\b[A-Z]\d{9}\b",
                score=0.8
            ),
            Pattern(
                name="german_health_insurance_flexible",
                regex=r"\b[A-Z][\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b",
                score=0.85
            ),
            Pattern(
                name="german_health_insurance_context",
                regex=r"(?i)\b(?:krankenversicherungs[^\w]*?nummer|kvnr|versicherten[^\w]*?nummer)[\s:]*([A-Z][\s\-]?\d{9})\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_HEALTH_INSURANCE",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_company_tax_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_company_tax_standard",
                regex=r"\b\d{2,3}/\d{3}/\d{4,5}\b",
                score=0.8
            ),
            Pattern(
                name="german_company_tax_flexible",
                regex=r"\b\d{2,3}[\s\-\/]\d{3}[\s\-\/]\d{4,5}\b",
                score=0.85
            ),
            Pattern(
                name="german_company_tax_context",
                regex=r"(?i)\b(?:steuernummer|st[^\w]*?nr)[\s:]*(\d{2,3}[\s\-\/]?\d{3}[\s\-\/]?\d{4,5})\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_COMPANY_TAX",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_vat_id_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_vat_id_standard",
                regex=r"\bDE\d{9}\b",
                score=0.9
            ),
            Pattern(
                name="german_vat_id_flexible",
                regex=r"\bDE[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b",
                score=0.9
            ),
            Pattern(
                name="german_vat_id_context",
                regex=r"(?i)\b(?:umsatzsteuer[^\w]*?identifikationsnummer|ust[^\w]*?idnr|vat[^\w]*?id)[\s:]*(?:de[\s\-]?)(\d{9})\b",
                score=0.98
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_VAT_ID",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_commercial_register_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_commercial_register_standard",
                regex=r"\bHR[AB][\s\-]?\d{4,6}\b",
                score=0.85
            ),
            Pattern(
                name="german_commercial_register_context",
                regex=r"(?i)\b(?:handelsregister[^\w]*?nummer|hrb|hra)[\s:]*([A-Z]*\d{4,6})\b",
                score=0.95
            ),
            Pattern(
                name="german_commercial_register_full",
                regex=r"(?i)\b(?:ag|gmbh|kg|ohg)[\s,]+(?:hrb|hra)[\s\-]?(\d{4,6})\b",
                score=0.9
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_COMMERCIAL_REGISTER",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_iban_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_iban_standard",
                regex=r"\bDE\d{2}\s?(?:\d{4}\s?){4}\d{2}\b",
                score=0.95
            ),
            Pattern(
                name="german_iban_continuous",
                regex=r"\bDE\d{20}\b",
                score=0.95
            ),
            Pattern(
                name="german_iban_flexible",
                regex=r"\bDE[\s\-]?\d{2}[\s\-]?(?:\d{4}[\s\-]?){4}\d{2}\b",
                score=0.9
            ),
            Pattern(
                name="german_iban_context",
                regex=r"(?i)\biban[\s:]*(?:de[\s\-]?)(\d{22})\b",
                score=0.98
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_IBAN",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_bic_swift_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="bic_swift_german",
                regex=r"\b[A-Z]{4}DE[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",
                score=0.9
            ),
            Pattern(
                name="bic_swift_context",
                regex=r"(?i)\b(?:bic|swift|bank[^\w]*?code)[\s:]*([A-Z]{4}DE[A-Z0-9]{2}(?:[A-Z0-9]{3})?)\b",
                score=0.95
            ),
            Pattern(
                name="bic_swift_flexible",
                regex=r"\b[A-Z]{4}[\s\-]?DE[\s\-]?[A-Z0-9]{2}[\s\-]?[A-Z0-9]{3}?\b",
                score=0.85
            )
        ]
        return PatternRecognizer(
            supported_entity="BIC_SWIFT",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_phone_recognizer(self) -> PatternRecognizer:
        patterns = [
            # More comprehensive mobile patterns
            Pattern(
                name="german_mobile_comprehensive",
                regex=r"\b(?:\+49[\s\-\.]?)?(?:0?1[567]\d[\s\-\.]?\d{7,8})\b",
                score=0.9
            ),
            # More comprehensive landline patterns
            Pattern(
                name="german_landline_comprehensive",
                regex=r"\b(?:\+49[\s\-\.]?)?(?:0[\s\-\.]?)?(?:[2-9]\d{1,4}[\s\-\.]?\d{6,8})\b",
                score=0.85
            ),
            # Special numbers
            Pattern(
                name="german_special_numbers",
                regex=r"\b(?:\+49[\s\-\.]?)?(?:0?(?:800|900|180\d)[\s\-\.]?\d{6,8})\b",
                score=0.9
            ),
            # Context-aware patterns
            Pattern(
                name="german_phone_context_enhanced",
                regex=r"(?i)\b(?:telefon|tel|mobil|handy|festnetz|fax)[\s\.:]*(?:nr\.?|nummer)?[\s\.:]*(\+?[\d\s\-\.()]{8,})\b",
                score=0.95
            ),
            # International format
            Pattern(
                name="german_phone_international",
                regex=r"\b\+49[\s\-\.]?\d{2,4}[\s\-\.]?\d{6,8}\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_PHONE_NUMBER",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_address_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Enhanced street patterns with Unicode support
            Pattern(
                name="german_street_comprehensive",
                regex=r"\b[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|gasse|weg|platz|allee|ring|hof|damm|park|ufer|berg|tal|grund)[\s\-]?\d+[a-zA-Z]?\b",
                score=0.9
            ),
            # Full address patterns
            Pattern(
                name="german_full_address",
                regex=r"\b[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|gasse|weg|platz|allee|ring|hof|damm)[\s\-]?\d+[a-zA-Z]?[\s,]*\d{5}[\s]+[A-ZÄÖÜ][a-zäöüß]+\b",
                score=0.95
            ),
            # Postal code + city
            Pattern(
                name="german_postal_city_enhanced",
                regex=r"\b\d{5}[\s]+[A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ][a-zäöüß]+)*\b",
                score=0.9
            ),
            # Context-aware address patterns
            Pattern(
                name="german_address_context",
                regex=r"(?i)\b(?:adresse|anschrift|wohnhaft|ansässig|wohnt)[\s:]*([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|gasse|weg|platz|allee)[\s\-]?\d+[a-zA-Z]?)\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_STREET_ADDRESS",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_id_card_recognizer(self) -> PatternRecognizer:
        patterns = [
            # More specific ID card patterns
            Pattern(
                name="german_id_card_new_format",
                regex=r"\b[CFGHJKLMNPRTVWXYZ]\d{8}[CFGHJKLMNPRTVWXYZ]\b",
                score=0.9
            ),
            Pattern(
                name="german_id_card_old_format",
                regex=r"\b\d{10}[A-Z]\b",
                score=0.85
            ),
            Pattern(
                name="german_id_card_flexible",
                regex=r"\b[A-Z0-9]{9,11}\b",
                score=0.7
            ),
            Pattern(
                name="german_id_card_context",
                regex=r"(?i)\b(?:personalausweis|ausweis[^\w]*?nr|id[^\w]*?card)[\s:]*([A-Z0-9]{9,11})\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_ID_CARD",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_passport_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_passport_new_format",
                regex=r"\b[CFGHJKLMNPRTVWXYZ]\d{8}\b",
                score=0.9
            ),
            Pattern(
                name="german_passport_old_format",
                regex=r"\b[CFGHJK][0-9CFGHJKLMNPRTVWXYZ]{8}\b",
                score=0.85
            ),
            Pattern(
                name="german_passport_context",
                regex=r"(?i)\b(?:reisepass|passport|pass[^\w]*?nr)[\s:]*([CFGHJKLMNPRTVWXYZ][0-9CFGHJKLMNPRTVWXYZ]{8})\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_PASSPORT",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_driving_license_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_driving_license_new",
                regex=r"\b[A-Z0-9]{11}\b",
                score=0.75
            ),
            Pattern(
                name="german_driving_license_old",
                regex=r"\b\d{7,11}\b",
                score=0.65
            ),
            Pattern(
                name="german_driving_license_context",
                regex=r"(?i)\b(?:führerschein|fahrerlaubnis|driving[^\w]*?license)[\s:]*([A-Z0-9]{7,11})\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_DRIVING_LICENSE",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_residence_permit_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_residence_permit_standard",
                regex=r"\b[A-Z]\d{9}[A-Z]\d\b",
                score=0.85
            ),
            Pattern(
                name="german_residence_permit_flexible",
                regex=r"\b[A-Z][\s\-]?\d{9}[\s\-]?[A-Z][\s\-]?\d\b",
                score=0.8
            ),
            Pattern(
                name="german_residence_permit_context",
                regex=r"(?i)\b(?:aufenthaltstitel|residence[^\w]*?permit|aufenthaltsgenehmigung)[\s:]*([A-Z]\d{9}[A-Z]\d)\b",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_RESIDENCE_PERMIT",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_bank_account_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_bank_account_context",
                regex=r"(?i)(?:kontonummer|konto[^\w]*?nr|account[^\w]*?number)[\s:]*(\d{8,12})",
                score=0.9
            ),
            Pattern(
                name="german_bank_account_blz",
                regex=r"(?i)(?:blz|bankleitzahl)[\s:]*(\d{8})[\s,]*(?:konto|account)[\s:]*(\d{8,12})",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_BANK_ACCOUNT",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_social_security_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="german_social_security_standard",
                regex=r"\b\d{2}[\s\-]?\d{6}[\s\-]?[A-Z][\s\-]?\d{3}\b",
                score=0.9
            ),
            Pattern(
                name="german_social_security_context",
                regex=r"(?i)(?:sozialversicherungsnummer|sv[^\w]*?nummer|social[^\w]*?security)[\s:]*(\d{2}[\s\-]?\d{6}[\s\-]?[A-Z][\s\-]?\d{3})",
                score=0.95
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_SOCIAL_SECURITY",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_date_of_birth_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Standard date patterns
            Pattern(
                name="german_date_dd_mm_yyyy",
                regex=r"\b(?:[0-3]?\d)[\.\-\/](?:[01]?\d)[\.\-\/](?:19|20)?\d{2}\b",
                score=0.8
            ),
            Pattern(
                name="german_date_iso",
                regex=r"\b(?:19|20)\d{2}[\-\/](?:[01]?\d)[\-\/](?:[0-3]?\d)\b",
                score=0.8
            ),
            # Context-aware - only capture the date
            Pattern(
                name="german_dob_context_enhanced",
                regex=r"(?i)(?:geburtstag|geb\.?|geboren|geburtsdatum|birth[^\w]*?date)[\s:]*(\d{1,2}[\.\-\/]\d{1,2}[\.\-\/]\d{2,4})",
                score=0.95
            ),
            Pattern(
                name="german_age_context",
                regex=r"(?i)(?:alter|jahre\s+alt|years\s+old)[\s:]*(\d{1,3})",
                score=0.85
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_DATE_OF_BIRTH",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_name_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Context-aware patterns - only capture the name
            Pattern(
                name="german_name_titles_enhanced",
                regex=r"(?i)(?:herr|frau|dr\.?|prof\.?|professor|doktor|ing\.?)[\s]+([A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ][a-zäöüß]+)*)",
                score=0.9
            ),
            Pattern(
                name="german_name_context_enhanced",
                regex=r"(?i)(?:name|heißt|ist|nennt\s+sich|mein\s+name)[\s:]*(?:der|die|das)?\s*([A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ][a-zäöüß]+)*)",
                score=0.85
            ),
            # Standard patterns without context
            Pattern(
                name="german_name_nobility",
                regex=r"\b([A-ZÄÖÜ][a-zäöüß]+[\s]+(?:von|van|de|zu|zur|am|zum)[\s]+[A-ZÄÖÜ][a-zäöüß]+)\b",
                score=0.9
            ),
            Pattern(
                name="german_double_names",
                regex=r"\b([A-ZÄÖÜ][a-zäöüß]+[\-][A-ZÄÖÜ][a-zäöüß]+)\b",
                score=0.85
            ),
            Pattern(
                name="german_signature_pattern",
                regex=r"(?i)(?:unterschrift|signature|gezeichnet|gez\.?)[\s:]*([A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ][a-zäöüß]+)*)",
                score=0.9
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_PERSON_NAME",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_credit_card_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Standard patterns
            Pattern(
                name="credit_card_flexible",
                regex=r"\b(?:\d[\s\-]*){13,19}\b",
                score=0.85
            ),
            Pattern(
                name="credit_card_formatted_spaces",
                regex=r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
                score=0.9
            ),
            # Brand-specific patterns
            Pattern(
                name="credit_card_visa",
                regex=r"\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
                score=0.95
            ),
            Pattern(
                name="credit_card_mastercard",
                regex=r"\b5[1-5]\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
                score=0.95
            ),
            Pattern(
                name="credit_card_amex",
                regex=r"\b3[47]\d{2}[\s\-]?\d{6}[\s\-]?\d{5}\b",
                score=0.95
            ),
            # Context-aware - only capture the card number
            Pattern(
                name="credit_card_context_enhanced",
                regex=r"(?i)(?:kreditkarte|credit[^\w]*?card|kartennummer|card[^\w]*?number)[\s:]*(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})",
                score=0.98
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_CREDIT_CARD",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_customer_id_recognizer(self) -> PatternRecognizer:
        patterns = [
            Pattern(
                name="customer_id_alphanumeric",
                regex=r"\b[A-Z]{1,3}[\-\.]?\d{6,12}\b",
                score=0.8
            ),
            Pattern(
                name="insurance_customer_ids",
                regex=r"\b(?:AOK|TK|BKK|DAK|IKK|KKH|BARMER|TECHNIKER)[\-\.]?\d{6,10}\b",
                score=0.9
            ),
            # Context-aware - only capture the ID
            Pattern(
                name="customer_id_context_enhanced",
                regex=r"(?i)(?:kundennummer|kunden[^\w]*?id|customer[^\w]*?number|customer[^\w]*?id|mitgliedsnummer)[\s:]*([A-Z0-9\-\.]{6,15})",
                score=0.95
            ),
            Pattern(
                name="bank_customer_id",
                regex=r"(?i)(?:sparkasse|deutsche\s+bank|commerzbank|volksbank)[\s\-]*(?:kunden[^\w]*?nr|customer[^\w]*?id)[\s:]*(\d{6,12})",
                score=0.9
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_CUSTOMER_ID",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_expiry_date_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Standard patterns
            Pattern(
                name="expiry_date_mm_yy_enhanced",
                regex=r"\b(?:0[1-9]|1[0-2])[\-\/](?:\d{2}|20\d{2})\b",
                score=0.75
            ),
            # Context-aware - only capture the date
            Pattern(
                name="expiry_date_context_enhanced",
                regex=r"(?i)(?:ablauf|gültig\s+bis|valid\s+(?:thru|until)|expires?|expiry|verfallsdatum)[\s:]*([01]?\d[\-\/](?:\d{2}|20\d{2}))",
                score=0.95
            ),
            Pattern(
                name="expiry_date_german_format_enhanced",
                regex=r"(?i)(?:gültig\s+bis|verfallsdatum|ablaufdatum)[\s:]*(\d{1,2}[\.\-\/]\d{1,2}[\.\-\/]\d{2,4})",
                score=0.95
            ),
            Pattern(
                name="card_expiry_pattern",
                regex=r"(?i)(?:valid\s+thru|exp|expires?)[\s:]*([01]?\d[\-\/]\d{2,4})",
                score=0.9
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_EXPIRY_DATE",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_postal_code_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Standard postal code
            Pattern(
                name="german_postal_code_standard",
                regex=r"\b\d{5}\b",
                score=0.7
            ),
            # Context-aware postal codes
            Pattern(
                name="german_postal_code_context_enhanced",
                regex=r"(?i)\b(?:plz|postleitzahl|postal[^\w]*?code|zip[^\w]*?code)[\s:]*(\d{5})\b",
                score=0.95
            ),
            # Postal code in address context
            Pattern(
                name="german_postal_code_address",
                regex=r"\b(\d{5})[\s]+[A-ZÄÖÜ][a-zäöüß]+(?:[\s\-][A-ZÄÖÜ][a-zäöüß]+)*\b",
                score=0.85
            ),
            # Location context
            Pattern(
                name="german_postal_code_location",
                regex=r"(?i)\b(?:in|aus|nach|von)[\s]+(\d{5})[\s]+[A-ZÄÖÜ][a-zäöüß]+\b",
                score=0.85
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_POSTAL_CODE",
            patterns=patterns,
            supported_language="de"
        )
    
    def _create_german_street_name_recognizer(self) -> PatternRecognizer:
        patterns = [
            # Enhanced street name patterns with comprehensive suffixes
            Pattern(
                name="german_street_name_comprehensive",
                regex=r"\b([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|gasse|weg|platz|allee|ring|hof|damm|park|ufer|berg|tal|grund|brücke|steig|pfad|chaussee|promenade))\b",
                score=0.85
            ),
            # Context-aware street names
            Pattern(
                name="german_street_name_context_enhanced",
                regex=r"(?i)\b(?:in\s+der|an\s+der|auf\s+der|wohnt\s+in|ansässig\s+in|adresse)[\s]*([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|gasse|weg|platz|allee|ring|hof|damm))\b",
                score=0.9
            ),
            # Street with house number
            Pattern(
                name="german_street_with_number_enhanced",
                regex=r"\b([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|gasse|weg|platz|allee|ring|hof|damm))[\s]+\d+[a-zA-Z]?\b",
                score=0.9
            ),
            # Famous streets pattern
            Pattern(
                name="german_famous_streets",
                regex=r"\b([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.?|platz|allee|ring|damm))(?=\s+(?:\d+|in|berlin|münchen|hamburg|köln))\b",
                score=0.85
            )
        ]
        return PatternRecognizer(
            supported_entity="DE_STREET_NAME",
            patterns=patterns,
            supported_language="de"
        )