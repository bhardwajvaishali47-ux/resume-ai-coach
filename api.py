import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from pipeline import analyze_resume
from chains.cover_letter import generate_cover_letter
from tools.jobs_api import get_jobs_for_profile
from agent.career_coach import build_career_coach, chat_with_coach
from auth.database import get_db, create_tables
from auth.models import User
from auth.auth_handler import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    get_current_user_email
)
from auth.google_oauth import get_google_auth_url, exchange_code_for_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("AI Resume Coach API started successfully")
    yield


app = FastAPI(
    title="AI Resume Coach API",
    description="Backend API for AI Resume Coach application",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

sessions = {}
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency — extracts and verifies the current user
    from the JWT token in the request header.
    Used to protect endpoints that require authentication.
    """
    token = credentials.credentials
    email = get_current_user_email(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


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


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    user_name: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "AI Resume Coach API is running"
    }


@app.post("/auth/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    User registration endpoint.
    Creates a new account with email and password.
    """
    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login instead."
        )

    hashed = hash_password(request.password)
    new_user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_email=new_user.email,
        user_name=new_user.full_name or ""
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint.
    Verifies credentials and returns JWT token.
    """
    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.hashed_password:
        raise HTTPException(
            status_code=401,
            detail="This account uses Google login. Please sign in with Google."
        )

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    from sqlalchemy.sql import func
    user.last_login = func.now()
    db.commit()

    token = create_access_token({"sub": user.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_email=user.email,
        user_name=user.full_name or ""
    )


@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the current logged in user's profile."""
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "created_at": str(current_user.created_at)
    }


@app.get("/auth/google/url")
def google_auth_url():
    """Returns the Google OAuth authorization URL."""
    url = get_google_auth_url()
    return {"url": url}


@app.post("/auth/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Handles the Google OAuth callback."""
    try:
        user_info = await exchange_code_for_token(code)

        email = user_info.get("email")
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Could not get email from Google"
            )

        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                email=email,
                full_name=user_info.get("full_name"),
                google_id=user_info.get("google_id"),
                profile_picture=user_info.get("profile_picture")
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_access_token({"sub": user.email})

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_email=user.email,
            user_name=user.full_name or ""
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Google authentication failed: {str(e)}"
        )


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Main analysis endpoint.
    Accepts PDF resume and job description.
    Returns complete match analysis.
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
    """Cover letter generation endpoint."""
    letter = generate_cover_letter(
        request.parsed_resume,
        request.job_description,
        request.match_result
    )
    return {"cover_letter": letter}


@app.post("/chat")
def chat(request: ChatRequest):
    """Chat endpoint for conversational career coaching."""
    session_id = request.session_id

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
    """Live job listings endpoint."""
    result = get_jobs_for_profile(
        request.parsed_resume,
        request.match_result,
        country=request.country,
        job_description=request.job_description
    )
    return result


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Deletes a chat session from memory."""
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