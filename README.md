# Resume Scanner API

AI-powered resume parsing and job matching system built with FastAPI and Google Gemini AI.

## Features

- **Resume Parsing**: Extract structured data from PDF
- **AI-Powered Extraction**: Uses Google Gemini AI for intelligent data extraction
- **Fallback Systems**: Regex and spaCy for reliable extraction when AI fails
- **Job Matching**: Semantic similarity matching between resumes and job descriptions
- **Bulk Processing**: Match multiple resumes against job descriptions
- **Skills Analysis**: Detailed skills matching and gap analysis

## Architecture

```
resume-scanner/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── routers/
│   │   ├── resume.py        # Resume upload & parsing API
│   │   └── job.py           # Job matching API
│   ├── services/
│   │   ├── parser.py        # File parsing (PDF/DOCX/TXT)
│   │   ├── extractor.py     # Regex + spaCy extraction
│   │   ├── gemini_ai.py     # Gemini AI integration
│   │   └── matcher.py       # Resume-job matching
│   └── utils/
│       └── skills.json      # Skills dictionary
├── uploads/                 # Temporary file storage
├── requirements.txt
├── .env                     # Environment variables
└── README.md
```

## Quick Start

### 1. Setup Environment

```bash
# Clone or create project directory
mkdir resume-scanner && cd resume-scanner

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Or run the setup script
python setup.py
```

### 2. Configure API Key

Create `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
UPLOAD_DIR=uploads/
MAX_FILE_SIZE=5242880
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Resume Processing

#### Upload Resume
```http
POST /api/upload-resume/
Content-Type: multipart/form-data

# Upload PDF, DOCX, or TXT file
```

**Response:**
```json
{
  "success": true,
  "message": "Resume parsed successfully",
  "data": {
    "file_id": "uuid-here",
    "original_filename": "resume.pdf",
    "parsed_data": {
      "personal_info": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-234-567-8900",
        "location": "New York, NY"
      },
      "skills": ["Python", "JavaScript", "React"],
      "work_experience": [...],
      "education": [...],
      "years_experience": 5
    }
  }
}
```

#### Parse Text
```http
POST /api/parse-text/
Content-Type: application/json

{
  "text": "Resume content as plain text..."
}
```

### Job Matching

#### Match Resume to Job
```http
POST /api/match-job/
Content-Type: application/json

{
  "resume_data": {...},
  "job_description": "Software Engineer position requiring Python..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "match_score": 85,
    "match_details": {
      "match_score": 85,
      "match_explanation": "Strong match based on...",
      "strengths": ["Python expertise", "React experience"],
      "gaps": ["Kubernetes experience missing"],
      "key_matching_skills": ["Python", "JavaScript"],
      "missing_skills": ["Kubernetes", "Docker"]
    }
  }
}
```

#### Bulk Match Resumes
```http
POST /api/bulk-match/
Content-Type: application/json

{
  "resumes": [
    {"data": {...}, "filename": "resume1.pdf"},
    {"data": {...}, "filename": "resume2.pdf"}
  ],
  "job_description": "Job requirements...",
  "top_n": 5
}
```

#### Analyze Job Description
```http
POST /api/analyze-job/
Content-Type: application/json

{
  "job_description": "Software Engineer position..."
}
```

### Utility Endpoints

#### Skills Match
```http
POST /api/skills-match/
Content-Type: application/json

{
  "resume_skills": ["Python", "React", "SQL"],
  "required_skills": ["Python", "JavaScript", "Docker"]
}
```

#### Supported Formats
```http
GET /api/supported-formats/
```

## How It Works

### 1. Resume Parsing Pipeline

```
File Upload → Text Extraction → AI Processing → Regex Fallback → Enhanced Data
```

1. **File Processing**: PyMuPDF for PDFs, python-docx for Word docs
2. **AI Extraction**: Gemini AI extracts structured JSON from resume text
3. **Fallback Extraction**: Regex patterns and spaCy NER for missing data
4. **Data Enhancement**: Combines AI and regex results for best accuracy

### 2. Job Matching Process

```
Resume Data + Job Description → Gemini AI Analysis → Match Score + Insights
```

1. **Semantic Analysis**: Gemini AI compares resume content with job requirements
2. **Multi-factor Scoring**: Skills (40%), Experience (25%), Education (15%), Domain (20%)
3. **Detailed Feedback**: Strengths, gaps, recommendations, and missing skills
4. **Ranking**: For bulk processing, resumes ranked by match score

## AI Integration

The system leverages Google Gemini AI for:

- **Structured Data Extraction**: Convert unstructured resume text to JSON
- **Semantic Job Matching**: Understand context and meaning, not just keywords
- **Skills Gap Analysis**: Identify missing skills and provide recommendations
- **Job Requirements Analysis**: Extract structured requirements from job descriptions

## Error Handling

- **File Validation**: Size limits, format checking
- **Graceful Fallbacks**: Regex/spaCy when AI fails
- **Detailed Error Messages**: Clear feedback for debugging
- **Cleanup**: Automatic file cleanup after processing

## Performance Considerations

- **File Size Limit**: 5MB default (configurable)
- **Bulk Processing Limit**: 50 resumes max
- **Rate Limiting**: Built into Gemini API
- **Memory Management**: Files processed and cleaned up immediately

## Environment Variables

```env
GEMINI_API_KEY=your_api_key          # Required: Google Gemini API key
UPLOAD_DIR=uploads/                  # Optional: Upload directory
MAX_FILE_SIZE=5242880               # Optional: Max file size (5MB)
```

## Dependencies

- **FastAPI**: Modern web framework
- **Google Generative AI**: Gemini AI integration
- **PyMuPDF**: PDF text extraction
- **python-docx**: Word document processing
- **spaCy**: Named entity recognition
- **Pydantic**: Data validation
- **Regex**: Pattern matching

## Error Codes

- **400**: Bad request (invalid file, missing data)
- **413**: File too large
- **422**: Cannot process file content
- **500**: Server error (AI API failures, processing errors)

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - see LICENSE file for details.
