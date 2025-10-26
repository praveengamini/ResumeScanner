import google.generativeai as genai
import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Updated model name
        self.model = genai.GenerativeModel('gemini-flash-latest')
    
    def extract_resume_data(self, resume_text: str) -> Optional[Dict]:
        """Extract structured data from resume text using Gemini AI"""
        prompt = f"""
        Extract structured information from this resume and return ONLY a valid JSON object with the following structure:

        {{
            "personal_info": {{
                "name": "Full name",
                "email": "email@example.com",
                "phone": "phone number",
                "location": "city, state/country",
                "linkedin": "linkedin profile if mentioned",
                "portfolio": "portfolio/website URL if mentioned"
            }},
            "summary": "Professional summary or objective",
            "skills": ["skill1", "skill2", "skill3"],
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "university/college name",
                    "year": "graduation year",
                    "gpa": "GPA if mentioned"
                }}
            ],
            "work_experience": [
                {{
                    "title": "job title",
                    "company": "company name",
                    "duration": "start date - end date",
                    "location": "work location",
                    "responsibilities": ["responsibility1", "responsibility2"]
                }}
            ],
            "projects": [
                {{
                    "name": "project name",
                    "description": "project description",
                    "technologies": ["tech1", "tech2"],
                    "duration": "project duration if mentioned"
                }}
            ],
            "certifications": ["certification1", "certification2"],
            "languages": ["language1", "language2"],
            "years_experience": "estimated total years of experience as number"
        }}

        Resume text:
        {resume_text}

        Return only the JSON object, no additional text or explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response to extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            # Parse JSON
            resume_data = json.loads(response_text)
            return resume_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini response: {e}")
            print(f"Raw response: {response_text}")
            return None
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    def calculate_ats_score(self, resume_data: Dict, job_description: str) -> Optional[Dict]:
        """Calculate ATS score and provide detailed recommendations"""
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyzer. Analyze this resume against the job description and provide a comprehensive ATS score and recommendations.

        Return ONLY a valid JSON object with this exact structure:

        {{
            "ats_score": 85,
            "score_breakdown": {{
                "keywords_match": 80,
                "experience_level": 90,
                "skills_alignment": 85,
                "education_fit": 70,
                "format_optimization": 95
            }},
            "recommendations": [
                "Add more specific technical keywords from the job description",
                "Quantify achievements with specific numbers and metrics",
                "Include relevant certifications mentioned in the job posting"
            ],
            "strengths": [
                "Strong technical background in required technologies",
                "Relevant work experience in similar roles",
                "Good educational background"
            ],
            "gaps": [
                "Missing specific technology X mentioned in job requirements",
                "No mention of required certification Y",
                "Limited experience with Z framework"
            ],
            "matching_keywords": ["Python", "React", "PostgreSQL", "AWS"],
            "missing_keywords": ["Docker", "Kubernetes", "CI/CD", "Microservices"],
            "overall_assessment": "Strong candidate with good technical fit. Recommended for interview with focus on missing technical areas."
        }}

        Resume Data:
        {json.dumps(resume_data, indent=2)}

        Job Description:
        {job_description}

        Scoring Criteria:
        - Keywords Match (30%): How many job-specific terms appear in resume
        - Experience Level (25%): Years of experience vs requirements
        - Skills Alignment (25%): Technical/soft skills match
        - Education Fit (10%): Degree requirements met
        - Format Optimization (10%): Resume structure and ATS-friendliness

        ATS Score Scale:
        - 90-100: Excellent match, likely to pass ATS screening
        - 80-89: Very good match, high chance of interview
        - 70-79: Good match, decent chance with improvements
        - 60-69: Fair match, needs significant improvements
        - Below 60: Poor match, major gaps to address

        Return only the JSON object.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response to extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            # Parse JSON
            ats_result = json.loads(response_text)
            
            # Ensure score is within valid range
            if "ats_score" in ats_result:
                ats_result["ats_score"] = max(0, min(100, ats_result["ats_score"]))
            
            return ats_result
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini response: {e}")
            print(f"Raw response: {response_text}")
            return None
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    def enhance_resume_data(self, ai_data: Dict, regex_data: Dict) -> Dict:
        """Enhance AI-extracted data with regex/spaCy fallbacks"""
        enhanced_data = ai_data.copy()
        
        # Fill missing personal info with regex data
        if not enhanced_data.get("personal_info", {}).get("email") and regex_data.get("emails"):
            if "personal_info" not in enhanced_data:
                enhanced_data["personal_info"] = {}
            enhanced_data["personal_info"]["email"] = regex_data["emails"][0]
        
        if not enhanced_data.get("personal_info", {}).get("phone") and regex_data.get("phones"):
            if "personal_info" not in enhanced_data:
                enhanced_data["personal_info"] = {}
            enhanced_data["personal_info"]["phone"] = regex_data["phones"][0]
        
        if not enhanced_data.get("personal_info", {}).get("name") and regex_data.get("persons"):
            if "personal_info" not in enhanced_data:
                enhanced_data["personal_info"] = {}
            enhanced_data["personal_info"]["name"] = regex_data["persons"][0]
        
        # Enhance skills with regex-found skills
        ai_skills = enhanced_data.get("skills", [])
        regex_skills = regex_data.get("skills", [])
        all_skills = list(set(ai_skills + regex_skills))
        enhanced_data["skills"] = all_skills
        
        # Add years of experience if missing
        if not enhanced_data.get("years_experience") and regex_data.get("years_experience"):
            enhanced_data["years_experience"] = regex_data["years_experience"]
        
        return enhanced_data