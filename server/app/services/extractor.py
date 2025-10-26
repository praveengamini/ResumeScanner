import re
import spacy
from typing import List, Dict, Optional
import json
import os

class RegexSpacyExtractor:
    def __init__(self):
        # Load spaCy model (download with: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError, TypeError):
            print("⚠️ spaCy model not available. Using regex-only extraction (Gemini AI still works!)")
            self.nlp = None
        
        # Load skills dictionary
        self.skills = self._load_skills()
    
    def _load_skills(self) -> List[str]:
        """Load skills from JSON file"""
        try:
            skills_path = os.path.join("app", "utils", "skills.json")
            with open(skills_path, 'r') as f:
                data = json.load(f)
                return data.get("skills", [])
        except Exception as e:
            print(f"Error loading skills: {e}")
            return []
    
    def extract_email(self, text: str) -> List[str]:
        """Extract email addresses using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Remove duplicates
    
    def extract_phone(self, text: str) -> List[str]:
        """Extract phone numbers using regex"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # General pattern
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (123) 456-7890
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',   # 123-456-7890
            r'\+\d{1,3}\s?\d{10,14}'            # +1 1234567890
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Clean and validate phone numbers
        cleaned_phones = []
        for phone in phones:
            # Remove non-numeric characters except +
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 10:  # Valid phone number should have at least 10 digits
                cleaned_phones.append(phone.strip())
        
        return list(set(cleaned_phones))
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return {"persons": [], "organizations": [], "locations": []}
        
        doc = self.nlp(text)
        
        persons = []
        organizations = []
        locations = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                persons.append(ent.text)
            elif ent.label_ == "ORG":
                organizations.append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:  # Geopolitical entities and locations
                locations.append(ent.text)
        
        return {
            "persons": list(set(persons)),
            "organizations": list(set(organizations)),
            "locations": list(set(locations))
        }
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills by matching against skills dictionary"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    def extract_years_experience(self, text: str) -> Optional[int]:
        """Extract years of experience using regex"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*\w+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                years = [int(match) for match in matches if match.isdigit()]
                if years:
                    return max(years)  # Return the highest years mentioned
        
        return None
    
    def extract_all(self, text: str) -> Dict:
        """Extract all information using regex and spaCy"""
        emails = self.extract_email(text)
        phones = self.extract_phone(text)
        entities = self.extract_entities(text)
        skills = self.extract_skills(text)
        years_exp = self.extract_years_experience(text)
        
        return {
            "emails": emails,
            "phones": phones,
            "persons": entities["persons"],
            "organizations": entities["organizations"],
            "locations": entities["locations"],
            "skills": skills,
            "years_experience": years_exp
        }