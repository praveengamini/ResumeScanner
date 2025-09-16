from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

from app.services.matcher import ResumeMatcher
from app.services.gemini_ai import GeminiAI

router = APIRouter()

# Initialize services
matcher = ResumeMatcher()
gemini_ai = GeminiAI()

class JobMatchRequest(BaseModel):
    resume_data: Dict
    job_description: str

class BulkMatchRequest(BaseModel):
    resumes: List[Dict]
    job_description: str
    top_n: Optional[int] = 10

class SkillsMatchRequest(BaseModel):
    resume_skills: List[str]
    required_skills: List[str]

@router.post("/match-job/")
async def match_resume_to_job(request: JobMatchRequest):
    """
    Calculate match score between a resume and job description
    """
    try:
        if not request.resume_data or not request.job_description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both resume data and job description are required"
            )
        
        # Calculate match using Gemini AI
        match_result = matcher.match_resume_to_job(
            request.resume_data, 
            request.job_description
        )
        
        if not match_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate match score. Please try again."
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Job match calculated successfully",
                "data": {
                    "match_score": match_result["match_score"],
                    "match_details": match_result,
                    "processing_timestamp": datetime.now().isoformat(),
                    "job_description_length": len(request.job_description),
                    "resume_name": request.resume_data.get("personal_info", {}).get("name", "Unknown")
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while matching: {str(e)}"
        )

@router.post("/bulk-match/")
async def bulk_match_resumes(request: BulkMatchRequest):
    """
    Match multiple resumes against a job description and rank them
    """
    try:
        if not request.resumes or not request.job_description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both resumes list and job description are required"
            )
        
        if len(request.resumes) > 50:  # Limit to prevent abuse
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 resumes can be processed at once"
            )
        
        # Add IDs to resumes if not present
        for i, resume in enumerate(request.resumes):
            if "id" not in resume:
                resume["id"] = f"resume_{i+1}"
            if "filename" not in resume:
                resume["filename"] = f"resume_{i+1}.pdf"
        
        # Rank resumes
        ranked_resumes = matcher.rank_resumes(request.resumes, request.job_description)
        
        # Get top N candidates
        top_candidates = ranked_resumes[:request.top_n]
        
        # Generate summary
        summary = matcher.generate_match_summary(ranked_resumes)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": f"Successfully matched {len(request.resumes)} resumes",
                "data": {
                    "total_resumes_processed": len(request.resumes),
                    "top_candidates": top_candidates,
                    "all_results": ranked_resumes,
                    "match_summary": summary,
                    "processing_timestamp": datetime.now().isoformat(),
                    "job_description_length": len(request.job_description)
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during bulk matching: {str(e)}"
        )

@router.post("/skills-match/")
async def calculate_skills_match(request: SkillsMatchRequest):
    """
    Calculate basic skills match percentage (backup method)
    """
    try:
        if not request.resume_skills or not request.required_skills:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both resume skills and required skills are required"
            )
        
        match_percentage = matcher.calculate_skill_match_percentage(
            request.resume_skills, 
            request.required_skills
        )
        
        # Find matching and missing skills
        resume_skills_lower = [skill.lower() for skill in request.resume_skills]
        required_skills_lower = [skill.lower() for skill in request.required_skills]
        
        matching_skills = []
        missing_skills = []
        
        for req_skill in request.required_skills:
            req_skill_lower = req_skill.lower()
            if any(req_skill_lower in resume_skill for resume_skill in resume_skills_lower):
                matching_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Skills match calculated successfully",
                "data": {
                    "match_percentage": round(match_percentage, 2),
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills,
                    "total_resume_skills": len(request.resume_skills),
                    "total_required_skills": len(request.required_skills),
                    "skills_matched": len(matching_skills),
                    "processing_timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calculating skills match: {str(e)}"
        )

@router.post("/analyze-job/")
async def analyze_job_description(job_description: str):
    """
    Analyze job description to extract key requirements using AI
    """
    try:
        if not job_description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is required"
            )
        
        prompt = f"""
        Analyze this job description and extract key information. Return ONLY a valid JSON object:

        {{
            "job_title": "extracted job title",
            "company": "company name if mentioned",
            "location": "job location",
            "employment_type": "full-time/part-time/contract/etc",
            "experience_level": "entry/mid/senior/executive",
            "required_skills": ["skill1", "skill2"],
            "preferred_skills": ["skill1", "skill2"],
            "education_requirements": ["degree requirement"],
            "years_experience_required": "number or range",
            "salary_range": "salary if mentioned",
            "key_responsibilities": ["responsibility1", "responsibility2"],
            "benefits": ["benefit1", "benefit2"],
            "industry": "industry/domain"
        }}

        Job Description:
        {job_description}

        Return only the JSON object.
        """
        
        response = gemini_ai.model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response to extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
        
        # Parse JSON
        import json
        job_analysis = json.loads(response_text)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Job description analyzed successfully",
                "data": {
                    "job_analysis": job_analysis,
                    "job_description_length": len(job_description),
                    "processing_timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse job analysis. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing job description: {str(e)}"
        )