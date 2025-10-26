from typing import Dict, List, Optional
from .gemini_ai import GeminiAI

class ResumeMatcher:
    def __init__(self):
        self.gemini_ai = GeminiAI()
    
    def match_resume_to_job(self, resume_data: Dict, job_description: str) -> Optional[Dict]:
        """
        Match resume to job description using Gemini AI
        Returns match score and detailed analysis
        """
        return self.gemini_ai.calculate_job_match_score(resume_data, job_description)
    
    def rank_resumes(self, resumes: List[Dict], job_description: str) -> List[Dict]:
        """
        Rank multiple resumes against a job description
        Returns list of resumes sorted by match score (highest first)
        """
        ranked_resumes = []
        
        for resume in resumes:
            match_result = self.match_resume_to_job(resume["data"], job_description)
            
            if match_result:
                resume_with_score = {
                    "resume_id": resume.get("id", "unknown"),
                    "filename": resume.get("filename", "unknown"),
                    "resume_data": resume["data"],
                    "match_score": match_result["match_score"],
                    "match_details": match_result
                }
                ranked_resumes.append(resume_with_score)
        
        # Sort by match score (descending)
        ranked_resumes.sort(key=lambda x: x["match_score"], reverse=True)
        return ranked_resumes
    
    def get_top_candidates(self, resumes: List[Dict], job_description: str, top_n: int = 5) -> List[Dict]:
        """
        Get top N candidates for a job
        """
        ranked = self.rank_resumes(resumes, job_description)
        return ranked[:top_n]
    
    def calculate_skill_match_percentage(self, resume_skills: List[str], required_skills: List[str]) -> float:
        """
        Calculate percentage of required skills present in resume
        This is a backup method for basic skill matching
        """
        if not required_skills:
            return 100.0
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matched_skills = 0
        for req_skill in required_skills_lower:
            if any(req_skill in resume_skill for resume_skill in resume_skills_lower):
                matched_skills += 1
        
        return (matched_skills / len(required_skills)) * 100
    
    def generate_match_summary(self, match_results: List[Dict]) -> Dict:
        """
        Generate a summary of match results for multiple resumes
        """
        if not match_results:
            return {"error": "No match results provided"}
        
        total_resumes = len(match_results)
        scores = [result["match_score"] for result in match_results]
        
        summary = {
            "total_resumes_analyzed": total_resumes,
            "average_match_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "excellent_matches": len([s for s in scores if s >= 80]),  # 80+ score
            "good_matches": len([s for s in scores if 60 <= s < 80]),   # 60-79 score
            "fair_matches": len([s for s in scores if 40 <= s < 60]),   # 40-59 score
            "poor_matches": len([s for s in scores if s < 40]),         # <40 score
            "top_3_candidates": match_results[:3] if len(match_results) >= 3 else match_results
        }
        
        return summary