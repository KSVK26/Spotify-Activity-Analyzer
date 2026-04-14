from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import List, Dict
from config import SPOTIFY_REDIRECT_URI, FRONTEND_URL
from spotify_auth import get_auth_url, get_token_from_code, get_spotify_client
from models import UserSession, get_db
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from analysis import analyze_listening_data, normalize_spotify_data
from schemas import AnalysisResult
from spotify_api import get_all_recently_played, get_top_artists, get_top_tracks
from spotify_auth import get_spotify_client
from upload import analyze_uploaded_data
from fastapi import UploadFile, File, Form


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

    # Redirect to frontend dashboard with session ID
    frontend_url = f"{FRONTEND_URL}/dashboard?session_id={session.id}"
    return RedirectResponse(url=frontend_url)

@app.post("/analyze") 
def analyze_tracks(tracks: List[Dict], start_date: str = None, end_date: str = None):
    """Analyze listening data and return stats"""
    df = normalize_spotify_data(tracks)
    result = analyze_listening_data(df, start_date, end_date)
    return result

@app.get("/api/recently-played")
def recently_played(session_id: str, hours: int = 24, db: Session = Depends(get_db)):
    """Fetch user's recently played tracks"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}, 404
    
    sp = get_spotify_client(session.access_token)
    tracks = get_all_recently_played(sp, hours)
    
    return {"tracks": tracks, "count": len(tracks)}

@app.get("/api/top-artists")
def top_artists(session_id: str, time_range: str = "medium_term", db: Session = Depends(get_db)):
    """Fetch user's top artists"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}, 404
    
    sp = get_spotify_client(session.access_token)
    artists = get_top_artists(sp, time_range)
    
    return {"artists": artists}

@app.get("/api/top-tracks")
def top_tracks_api(session_id: str, time_range: str = "medium_term", db: Session = Depends(get_db)):
    """Fetch user's top tracks"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}, 404
    
    sp = get_spotify_client(session.access_token)
    tracks = get_top_tracks(sp, time_range)
    
    return {"tracks": tracks}

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    start_date: str = Form(None),
    end_date: str = Form(None)
):
    """Upload and analyze Spotify JSON files"""
    contents = []
    for file in files:
        content = await file.read()
        contents.append(content.decode('utf-8'))
    
    result = analyze_uploaded_data(contents, start_date, end_date)
    return result