from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import uuid
import aiofiles
from datetime import datetime

from app.services.parser import ResumeParser
from app.services.extractor import RegexSpacyExtractor
from app.services.gemini_ai import GeminiAI

router = APIRouter()

# Initialize services
parser = ResumeParser()
extractor = RegexSpacyExtractor()
gemini_ai = GeminiAI()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 5242880))  # 5MB default

def validate_file(filename: str, file_size: int) -> None:
    """Validate uploaded file"""
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
        )
    
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file
    Returns structured resume data extracted using AI and regex
    """
    try:
        # Validate file
        file_size = 0
        content = await file.read()
        file_size = len(content)
        validate_file(file.filename, file_size)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{file_id}{file_extension}"
        
        # Save file
        upload_dir = os.getenv("UPLOAD_DIR", "uploads/")
        file_path = os.path.join(upload_dir, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Extract text from file
        resume_text = parser.extract_text(file_path)
        if not resume_text:
            # Clean up file
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract text from the uploaded file"
            )
        
        # Extract structured data using Gemini AI
        ai_data = gemini_ai.extract_resume_data(resume_text)
        
        # Extract fallback data using regex and spaCy
        regex_data = extractor.extract_all(resume_text)
        
        # Enhance AI data with regex fallbacks
        if ai_data:
            final_data = gemini_ai.enhance_resume_data(ai_data, regex_data)
        else:
            # Fallback to basic structure if AI fails
            final_data = {
                "personal_info": {
                    "name": regex_data.get("persons", [None])[0],
                    "email": regex_data.get("emails", [None])[0],
                    "phone": regex_data.get("phones", [None])[0],
                    "location": regex_data.get("locations", [None])[0] if regex_data.get("locations") else None
                },
                "skills": regex_data.get("skills", []),
                "years_experience": regex_data.get("years_experience"),
                "organizations": regex_data.get("organizations", []),
                "summary": "Could not extract summary using AI",
                "education": [],
                "work_experience": [],
                "projects": [],
                "certifications": [],
                "languages": []
            }
        
        # Clean up uploaded file (optional - you might want to keep it)
        try:
            os.remove(file_path)
        except:
            pass
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Resume parsed successfully",
                "data": {
                    "file_id": file_id,
                    "original_filename": file.filename,
                    "parsed_data": final_data,
                    "raw_text_length": len(resume_text),
                    "processing_timestamp": datetime.now().isoformat(),
                    "extraction_methods_used": {
                        "gemini_ai": ai_data is not None,
                        "regex_spacy": True
                    }
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if it exists
        try:
            if 'file_path' in locals():
                os.remove(file_path)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )

@router.post("/parse-text/")
async def parse_resume_text(text: str):
    """
    Parse resume from raw text (alternative to file upload)
    """
    try:
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume text is too short or empty"
            )
        
        # Extract structured data using Gemini AI
        ai_data = gemini_ai.extract_resume_data(text)
        
        # Extract fallback data using regex and spaCy
        regex_data = extractor.extract_all(text)
        
        # Enhance AI data with regex fallbacks
        if ai_data:
            final_data = gemini_ai.enhance_resume_data(ai_data, regex_data)
        else:
            # Fallback structure
            final_data = {
                "personal_info": {
                    "name": regex_data.get("persons", [None])[0],
                    "email": regex_data.get("emails", [None])[0],
                    "phone": regex_data.get("phones", [None])[0],
                    "location": regex_data.get("locations", [None])[0] if regex_data.get("locations") else None
                },
                "skills": regex_data.get("skills", []),
                "years_experience": regex_data.get("years_experience"),
                "organizations": regex_data.get("organizations", []),
                "summary": "Could not extract summary using AI",
                "education": [],
                "work_experience": [],
                "projects": [],
                "certifications": [],
                "languages": []
            }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Resume text parsed successfully",
                "data": {
                    "parsed_data": final_data,
                    "raw_text_length": len(text),
                    "processing_timestamp": datetime.now().isoformat(),
                    "extraction_methods_used": {
                        "gemini_ai": ai_data is not None,
                        "regex_spacy": True
                    }
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the resume text: {str(e)}"
        )

@router.get("/supported-formats/")
async def get_supported_formats():
    """
    Get list of supported file formats
    """
    return {
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size_bytes": MAX_FILE_SIZE,
        "max_file_size_mb": round(MAX_FILE_SIZE / (1024 * 1024), 2)
    }