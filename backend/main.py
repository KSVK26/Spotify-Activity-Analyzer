from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import SPOTIFY_REDIRECT_URI
from spotify_auth import get_auth_url, get_token_from_code, get_spotify_client
from models import UserSession, get_db
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

app = FastAPI(title="Spotify Activity Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Spotify Activity Analyzer API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/auth/login")
def login():
    """Get Spotify OAuth URL"""
    auth_url = get_auth_url()
    return {"auth_url": auth_url}

@app.get("/callback")
def callback(code: str, error: str = None, db: Session = Depends(get_db)):
    """Handle OAuth callback from Spotify"""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    token_info = get_token_from_code(code)

    if not token_info:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    # Get user info from Spotify
    sp = get_spotify_client(token_info["access_token"])
    user = sp.current_user()

    # Create session
    session = UserSession(
        id=str(uuid.uuid4()),
        spotify_user_id=user["id"],
        access_token=token_info["access_token"],
        refresh_token=token_info.get("refresh_token", ""),
        token_expires_at=datetime.utcnow() + timedelta(seconds=token_info["expires_in"]),
    )

    db.add(session)
    db.commit()

    # Redirect to frontend with session ID (frontend URL will be added later)
    return {
        "status": "success",
        "session_id": session.id,
        "user_id": user["id"],
        "message": "Successfully authenticated with Spotify"
    }