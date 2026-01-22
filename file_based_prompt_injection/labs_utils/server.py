import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import PyPDF2

from database import (
    init_db,
    close_db,
    get_all_candidates,
    get_candidate_by_id,
    create_candidate,
    get_all_candidates_summary
)
from ai_analyzer import analyze_resume_with_ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    await close_db()
    print("❌ Database connections closed")


app = FastAPI(title="Resume Screening API", lifespan=lifespan)


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract all text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {str(e)}")


@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    name: str = "Unknown",
    lastname: str = "Unknown",
    email: str = "unknown@email.com",
    position: str = "Software Engineer"
):
    """
    Upload and analyze a resume PDF.
    Returns hiring decision and saves candidate to database.
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Read and extract text from PDF
    pdf_content = await file.read()
    resume_text = extract_text_from_pdf(pdf_content)
    
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    # Get all candidates context (VULNERABLE - exposes sensitive data to AI)
    candidates_context = await get_all_candidates_summary()
    
    # Analyze with AI
    try:
        decision_data = await analyze_resume_with_ai(
            resume_text=resume_text,
            position=position,
            candidates_context=candidates_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    
    # Save to database
    new_candidate = await create_candidate(
        name=name,
        lastname=lastname,
        email=email,
        position=position,
        status=decision_data["decision"],
        priority=decision_data["priority"],
        salary_offer=decision_data["salary_offer"],
        security_clearance=decision_data["security_clearance"],
        internal_notes=decision_data["reasoning"]
    )
    
    return JSONResponse(content={
        "candidate_id": new_candidate.id,
        "name": name,
        "lastname": lastname,
        "decision": decision_data["decision"],
        "status": decision_data["decision"],
        "priority": decision_data["priority"],
        "salary_offer": decision_data["salary_offer"],
        "security_clearance": decision_data["security_clearance"],
        "message": "Candidate analysis complete",
        "ai_reasoning": decision_data["reasoning"]
    })


@app.get("/candidates")
async def list_candidates():
    """Get all candidates from database"""
    candidates = await get_all_candidates()
    return {
        "candidates": [candidate.to_dict() for candidate in candidates]
    }


@app.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: int):
    """Get specific candidate details"""
    candidate = await get_candidate_by_id(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate.to_dict()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "resume-screening-api"}