import os
import tempfile
import uuid # UUID — Universally Unique Identifier. Generates a random string like "550e8400-e29b-41d4-a716-446655440000". Statistically impossible to generate the same ID twice. Used to uniquely identify each user's session.
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv

from pipeline import analyze_resume
from chains.cover_letter import generate_cover_letter
from tools.jobs_api import get_jobs_for_profile
from agent.career_coach import build_career_coach, chat_with_coach

load_dotenv()


#Creates the FastAPI application. The title and description appear automatically in the API documentation at http://localhost:8000/docs.
app = FastAPI(
    title="AI Resume Coach API",
    description="Backend API for AI Resume Coach application",
    version="1.0.0"
)

# CORS MIDDLEWARE
#CORS — Cross Origin Resource Sharing. When Streamlit (port 8501) calls FastAPI (port 8000), the browser blocks it by default because they are on different ports — considered different origins. CORS middleware tells FastAPI to allow requests from any origin. allow_origins=["*"] means allow all origins. In production you would restrict this to your specific domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

sessions = {}

# pydantic model
# Pydantic models define the shape of request data. FastAPI automatically validates incoming JSON against these models. If someone sends a request missing job_description, FastAPI returns a clear error before your code even runs. This is automatic input validation — you get it for free.
class CoverLetterRequest(BaseModel):
    parsed_resume: dict
    job_description: str
    match_result: dict


class ChatRequest(BaseModel):
    message: str
    session_id: str
    parsed_resume: dict
    job_description: str
    match_result: dict


class JobsRequest(BaseModel):
    parsed_resume: dict
    match_result: dict
    job_description: str
    country: str = "in"


# Endpoint decorators

#@app.get("/health") — this function handles GET requests to /health.
#@app.post("/analyze") — this function handles POST requests to /analyze.
#The decorator connects the URL path to the function. When a request arrives at that path with that method, FastAPI calls the function automatically.

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns 200 if server is running correctly.
    Used to verify the API is up before making other calls.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "AI Resume Coach API is running"
    }


@app.post("/analyze")
#Async file upload
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Main analysis endpoint.
    Accepts PDF resume and job description.
    Returns complete match analysis.

    Input:  multipart form with PDF file + job_description text
    Output: {parsed_resume, match_result}
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = analyze_resume(tmp_path, job_description)
    finally:
        os.unlink(tmp_path)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/cover-letter")
def cover_letter(request: CoverLetterRequest):
    """
    Cover letter generation endpoint.
    Takes parsed resume, job description, and match result.
    Returns a personalised cover letter as text.

    Input:  {parsed_resume, job_description, match_result}
    Output: {cover_letter: "letter text here"}
    """
    letter = generate_cover_letter(
        request.parsed_resume,
        request.job_description,
        request.match_result
    )
    return {"cover_letter": letter}


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Chat endpoint for conversational career coaching.
    Maintains session state in memory using session_id.
    First message builds the agent with full context.
    Subsequent messages use existing agent from session.

    Input:  {message, session_id, parsed_resume,
             job_description, match_result}
    Output: {response: "agent response text",
             session_id: "session id"}
    """
    session_id = request.session_id
    
    # sessions is a Python dictionary stored in memory. Each key is a session ID — a unique string identifying one user's conversation. The value is the agent and history for that session.
    
    # When a new session ID arrives, we build a fresh agent. When an existing session ID arrives, we reuse the existing agent with its full history.
    
    # This is in-memory session storage. It works but has one limitation — if the server restarts, all sessions are lost.

    if session_id not in sessions:
        agent, history = build_career_coach(
            request.parsed_resume,
            request.job_description,
            request.match_result
        )
        sessions[session_id] = {
            "agent": agent,
            "history": history
        }

    agent = sessions[session_id]["agent"]
    response = chat_with_coach(agent, request.message)

    return {
        "response": response,
        "session_id": session_id
    }


@app.post("/jobs")
def jobs(request: JobsRequest):
    """
    Live job listings endpoint.
    Searches Adzuna for jobs matching the candidate profile.

    Input:  {parsed_resume, match_result, job_description, country}
    Output: {keywords_used, jobs_found, jobs: [...]}
    """
    result = get_jobs_for_profile(
        request.parsed_resume,
        request.match_result,
        country=request.country,
        job_description=request.job_description
    )
    return result


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """
    Deletes a chat session from memory.
    Called when user starts a new analysis.
    Prevents memory from growing indefinitely.

    Input:  session_id in URL path
    Output: {message: "Session deleted"}
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} deleted"}
    return {"message": "Session not found"}


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )