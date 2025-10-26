from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid
import json
import aiofiles
from datetime import datetime

from app.services.parser import ResumeParser
from app.services.gemini_ai import GeminiAI

# Load environment variables
load_dotenv()

app = FastAPI(title="ATS Resume Scanner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
parser = ResumeParser()
gemini_ai = GeminiAI()

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 5242880  # 5MB

@app.get("/")
async def root():
    return {"message": "ATS Resume Scanner API", "status": "running"}

@app.post("/scan-resume/")
async def scan_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Upload resume + job description → Get ATS score and recommendations
    """
    try:
        # Validate file
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Max size: 5MB"
            )
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}{file_extension}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Extract text
        resume_text = parser.extract_text(file_path)
        if not resume_text:
            os.remove(file_path)
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from file"
            )
        
        # Parse resume using AI
        resume_data = gemini_ai.extract_resume_data(resume_text)
        if not resume_data:
            os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail="Failed to parse resume. Please try again."
            )
        
        # Calculate ATS score
        ats_result = gemini_ai.calculate_ats_score(resume_data, job_description)
        if not ats_result:
            os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail="Failed to calculate ATS score. Please try again."
            )
        
        # Clean up file
        os.remove(file_path)
        
        return {
            "success": True,
            "candidate_name": resume_data.get("personal_info", {}).get("name", "Unknown"),
            "ats_score": ats_result["ats_score"],
            "score_breakdown": ats_result["score_breakdown"],
            "recommendations": ats_result["recommendations"],
            "strengths": ats_result["strengths"],
            "gaps": ats_result["gaps"],
            "matching_keywords": ats_result["matching_keywords"],
            "missing_keywords": ats_result["missing_keywords"],
            "overall_assessment": ats_result["overall_assessment"],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if 'file_path' in locals():
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )