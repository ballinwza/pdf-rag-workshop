import re
# from presidio_analyzer import AnalyzerEngine
# from presidio_anonymizer import AnonymizerEngine

class DataSanitizerService:
    def __init__(self, custom_keywords: list[str] = []):
        # Presidio NER engine
        # self.analyzer = AnalyzerEngine()
        # self.anonymizer = AnonymizerEngine()
        
        # Setup custom keyword blacklist
        self.custom_keywords = custom_keywords or []
        
        # Setup Regx
        self.regx_patterns = {
            r'\b\d{13}\b': '[REDACTED_NATIONAL_ID]',
            r'\b0\d{1,2}[- ]?\d{3,4}[- ]?\d{4}\b': '[REDACTED_PHONE]',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[REDACTED_EMAIL]'
        }
        
    def sanitize(self, text:str) -> str:
        cleaned_text = text
        
        # Regx
        for pattern, replacment in self.regx_patterns.items():
            cleaned_text = re.sub(pattern, replacment, cleaned_text)
            
        # Blacklist
        for kw in self.custom_keywords:
            if kw.strip():
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
                cleaned_text = pattern.sub("[REDACTED_CONFIDENTIAL_TERM]", cleaned_text)
        
        # Presidio NER        
        # try:
        #     results = self.analyzer.analyze(
        #         text=cleaned_text,
        #         entities=["PERSON", "LOCATION", "ORGANIZATION"],
        #         language="en"
        #     )
        #     anonymized = self.anonymizer.anonymize(text=cleaned_text, analyzer_results=results)
        #     cleaned_text = anonymized.text
        # except Exception:
        #     pass

        return cleaned_text