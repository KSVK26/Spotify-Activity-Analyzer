# Spotify Activity Analyzer Website - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack web application where users connect their Spotify account, analyze listening activity with customizable date ranges, and share "Wrapped-style" stats/visualizations on social media.

**Architecture:** Three-tier web app: React/Next.js frontend (dashboard + shareable cards), FastAPI backend (Spotify OAuth + data processing), PostgreSQL database (user sessions + cached analysis). Existing Python analysis functions will be adapted as API endpoints returning JSON for client-side chart rendering.

**Tech Stack:**
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts/Chart.js, shadcn/ui components
- **Backend:** FastAPI, Python 3.11+, Spotipy (Spotify OAuth), pandas (data analysis)
- **Database:** PostgreSQL (production) / SQLite (development)
- **Deployment:** Vercel (frontend), Railway/Render (backend + DB)
- **Social Sharing:** Open Graph images, Twitter Cards, PNG export via html2canvas

---

## Context

**Why this project:** Transform an existing CLI-based Spotify streaming analyzer into a modern web application. The current `spotify_activity_analyzer.py` already implements solid analysis logic (top artists, weekday patterns, listening time trends) but requires manual JSON downloads from Spotify and produces static matplotlib plots.

**What prompted this:** User wants to build a "Spotify Wrapped but customizable" - users pick any date range, not just year-end. The 1-2 month timeline suggests a focused MVP with core features first, then polish.

**Intended outcome:** A production-ready website where users:
1. Log in with Spotify OAuth
2. Select any date range (last 7 days, last month, custom dates)
3. See interactive visualizations of their listening habits
4. Generate shareable "cards" for social media (Instagram Stories, Twitter, etc.)

---

## Feature Recommendations (Prioritized for 1-2 Month Build)

### Phase 1: Core MVP (Weeks 1-3)
- Spotify OAuth authentication
- Import streaming history (manual JSON upload OR Spotify API "Recently Played")
- Date range picker (preset ranges + custom)
- Basic stats dashboard: top artists, top tracks, total listening time
- 3-4 key visualizations (listening over time, weekday patterns, top artists)

### Phase 2: Wrapped-Style Features (Weeks 4-6)
- "Your Top X%" metrics (e.g., "You're in the top 5% of Taylor Swift listeners")
- Genre breakdown pie chart
- "Artist consistency" score (days listened / total days)
- Shareable cards with branded templates (Instagram Story size: 1080x1920)
- Download as PNG / direct share to Twitter

### Phase 3: Polish & Growth (Weeks 7-8)
- User profiles (public/private toggle)
- Shareable links to view someone's stats
- Comparative stats ("You listened to 50% more pop than average")
- Email weekly/monthly digests
- Dark mode, animations, loading states

---

## Critical Files to Modify/Create

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app entry point, OAuth routes |
| `backend/spotify_client.py` | Spotify API wrapper (fetch listening history) |
| `backend/analysis.py` | Port existing pandas functions as API endpoints |
| `backend/models.py` | SQLAlchemy database models (User, Session, Analysis) |
| `backend/config.py` | Environment variables (Spotify credentials, DB URL) |
| `frontend/app/page.tsx` | Landing page + OAuth login |
| `frontend/app/dashboard/page.tsx` | Main analysis dashboard |
| `frontend/components/DateRangePicker.tsx` | Date range selection UI |
| `frontend/components/StatsCard.tsx` | Reusable stat display component |
| `frontend/components/charts/*.tsx` | Individual chart components |
| `frontend/lib/spotify.ts` | Frontend Spotify API calls |
| `frontend/lib/export.ts` | PNG export + social sharing |

---

## Existing Code to Reuse

From `spotify_activity_analyzer.py`:

| Function | Reuse Strategy |
|----------|----------------|
| `ms2hr()` | Copy as pure Python utility |
| `file2df()` | Adapt for JSON upload handler |
| `load_over_time()` | Backend API endpoint returning `{date: hours}` |
| `avg_day_load()` | Backend endpoint returning weekday stats JSON |
| `top_artists()` | Backend endpoint; frontend renders dual-axis chart |
| `top_tracks()` | Backend endpoint |
| `top_artists_most_days()` | "Consistency score" feature |
| Column renaming logic | Data normalization middleware |

**Do NOT reuse:** `plot_df()`, `plt.show()` - frontend will render charts with Recharts

---

## Verification (End-to-End Testing)

1. **Local Development:**
   ```bash
   # Backend
   cd backend
   cp .env.example .env  # Add Spotify Client ID/Secret
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm install
   npm run dev
   ```

2. **OAuth Flow:** Visit `http://localhost:3000`, click "Connect Spotify", verify redirect to Spotify and back

3. **Analysis:** Select date range, verify dashboard shows:
   - At least 4 charts rendering
   - Stats match expected values (spot-check against raw data)

4. **Social Share:** Click "Share", verify PNG download contains all visual elements

5. **Production Deploy:**
   - Backend: `railway up` (or Render deploy)
   - Frontend: `vercel deploy`
   - Verify OAuth redirect URLs match production domains

---

## Implementation Tasks

### Task 1: Project Setup - Backend Foundation

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/config.py`
- Create: `backend/.env.example`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
spotipy==2.23.0
pandas==2.1.4
sqlalchemy==2.0.25
alembic==1.13.1
```

- [ ] **Step 2: Run test to verify file is valid**

```bash
cd backend
pip install -r requirements.txt
```
Expected: All packages install successfully

- [ ] **Step 3: Create config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/callback")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spotify_analyzer.db")
```

- [ ] **Step 4: Create .env.example**

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback
DATABASE_URL=sqlite:///./spotify_analyzer.db
```

- [ ] **Step 5: Create main.py with basic FastAPI app**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import SPOTIFY_REDIRECT_URI

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
```

- [ ] **Step 6: Test the server starts**

```bash
cd backend
uvicorn main:app --reload
```
Expected: Server runs at http://localhost:8000, visit `/health` returns `{"status":"healthy"}`

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: set up FastAPI backend foundation"
```

---

### Task 2: Spotify OAuth Authentication

**Files:**
- Create: `backend/spotify_auth.py`
- Modify: `backend/main.py`
- Create: `backend/models.py`

- [ ] **Step 1: Create database models in models.py**

```python
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    spotify_user_id = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Create tables**

```bash
cd backend
python -c "from models import Base, engine; Base.metadata.create_all(bind=engine)"
```
Expected: No errors, database file created

- [ ] **Step 3: Create spotify_auth.py**

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-read-recently-played user-top-read user-read-playback-state",
        open_browser=False,
        cache_file=None,
    )

def get_auth_url():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def get_token_from_code(code: str):
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)
    return token_info

def get_spotify_client(access_token: str):
    return spotipy.Spotify(auth=access_token)
```

- [ ] **Step 4: Add OAuth routes to main.py**

```python
# Add to imports
from spotify_auth import get_auth_url, get_token_from_code, get_spotify_client
from models import UserSession, get_db
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

# Add these routes to main.py

@app.get("/auth/login")
def login():
    """Get Spotify OAuth URL"""
    auth_url = get_auth_url()
    return {"auth_url": auth_url}

@app.get("/callback")
def callback(code: str, db: Session = next(get_db())):
    """Handle OAuth callback from Spotify"""
    token_info = get_token_from_code(code)
    
    # Get user info
    sp = get_spotify_client(token_info["access_token"])
    user = sp.current_user()
    
    # Create or update session
    session_id = str(uuid.uuid4())
    session = UserSession(
        id=session_id,
        spotify_user_id=user["id"],
        access_token=token_info["access_token"],
        refresh_token=token_info.get("refresh_token", ""),
        token_expires_at=datetime.now() + timedelta(seconds=token_info["expires_in"]),
    )
    db.add(session)
    db.commit()
    
    return {"session_id": session_id, "user_id": user["id"]}
```

- [ ] **Step 5: Test OAuth flow**

```bash
# Start server
uvicorn main:app --reload

# Get auth URL
curl http://localhost:8000/auth/login
```
Expected: Returns `{"auth_url": "https://accounts.spotify.com/authorize?..."}`

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: implement Spotify OAuth authentication"
```

---

### Task 3: Data Analysis Module (Port Existing Functions)

**Files:**
- Create: `backend/analysis.py`
- Create: `backend/schemas.py`

- [ ] **Step 1: Create Pydantic schemas in schemas.py**

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ListeningDay(BaseModel):
    date: str
    hours: float

class ArtistStats(BaseModel):
    artistName: str
    noStreams: int
    streamTimeHr: float

class TrackStats(BaseModel):
    artistName: str
    trackName: str
    noStreams: int
    streamTimeHr: float
    fullName: Optional[str] = None

class WeekdayStats(BaseModel):
    weekday: str
    hrPlayedAvg: float
    noStreamsAvg: float
    lenStreamsAvgMin: float

class AnalysisResult(BaseModel):
    listening_over_time: List[ListeningDay]
    top_artists: List[ArtistStats]
    top_tracks: List[TrackStats]
    weekday_stats: List[WeekdayStats]
    total_hours: float
    total_streams: int
```

- [ ] **Step 2: Create analysis.py with ported functions**

```python
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

def ms2hr(ms_val: float) -> float:
    """Convert milliseconds to hours"""
    return ms_val / (1000 * 60 * 60)

def normalize_spotify_data(tracks: List[Dict]) -> pd.DataFrame:
    """Normalize Spotify API track data into DataFrame"""
    df = pd.DataFrame(tracks)
    
    # Handle both API data and uploaded JSON formats
    if 'track' in df.columns:
        # Spotify API format - track is nested
        df['artistName'] = df['track'].apply(lambda x: x['artists'][0]['name'] if x and x.get('artists') else 'Unknown')
        df['trackName'] = df['track'].apply(lambda x: x['name'] if x else 'Unknown')
        df['msPlayed'] = df['track'].apply(lambda x: x['duration_ms'] if x else 0)
        df['endTime'] = pd.to_datetime(df['played_at'])
    else:
        # Uploaded JSON format
        df = df.rename(columns={
            'ts': 'endTime',
            'master_metadata_album_artist_name': 'artistName',
            'master_metadata_track_name': 'trackName',
            'ms_played': 'msPlayed'
        })
        df['endTime'] = pd.to_datetime(df['endTime'])
    
    return df

def load_over_time(df: pd.DataFrame) -> List[Dict]:
    """Calculate total listening time per day"""
    df = df.copy()
    df['date'] = pd.to_datetime(df['endTime']).dt.strftime('%Y-%m-%d')
    
    df_time = df.groupby('date')['msPlayed'].sum().reset_index()
    df_time['hours'] = df_time['msPlayed'] / (1000 * 60 * 60)
    
    return [
        {"date": row['date'], "hours": round(row['hours'], 2)}
        for _, row in df_time.iterrows()
    ]

def get_top_artists(df: pd.DataFrame, top: int = 10) -> List[Dict]:
    """Get top artists by stream count"""
    df_top = df.groupby('artistName').agg({
        'endTime': 'count',
        'msPlayed': 'sum'
    }).reset_index()
    df_top.columns = ['artistName', 'noStreams', 'streamTimeMs']
    df_top['streamTimeHr'] = df_top['streamTimeMs'] / (1000 * 60 * 60)
    df_top = df_top.sort_values('noStreams', ascending=False).head(top)
    
    return [
        {
            "artistName": row['artistName'],
            "noStreams": int(row['noStreams']),
            "streamTimeHr": round(row['streamTimeHr'], 2)
        }
        for _, row in df_top.iterrows()
    ]

def get_top_tracks(df: pd.DataFrame, top: int = 10) -> List[Dict]:
    """Get top tracks by stream count"""
    df_top = df.groupby(['artistName', 'trackName']).agg({
        'endTime': 'count',
        'msPlayed': 'sum'
    }).reset_index()
    df_top.columns = ['artistName', 'trackName', 'noStreams', 'streamTimeMs']
    df_top['streamTimeHr'] = df_top['streamTimeMs'] / (1000 * 60 * 60)
    df_top = df_top.sort_values('noStreams', ascending=False).head(top)
    df_top['fullName'] = df_top['artistName'] + " - " + df_top['trackName']
    
    return [
        {
            "artistName": row['artistName'],
            "trackName": row['trackName'],
            "noStreams": int(row['noStreams']),
            "streamTimeHr": round(row['streamTimeHr'], 2),
            "fullName": row['fullName']
        }
        for _, row in df_top.iterrows()
    ]

def get_weekday_stats(df: pd.DataFrame) -> List[Dict]:
    """Get streaming patterns by day of week"""
    df = df.copy()
    df['weekday'] = pd.to_datetime(df['endTime']).dt.day_name()
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    df_stats = df.groupby('weekday').agg({
        'endTime': 'count',
        'msPlayed': 'sum'
    }).reset_index()
    
    df_stats['dayCount'] = df_stats['endTime']  # Number of weeks with data
    df_stats['hrPlayed'] = df_stats['msPlayed'] / (1000 * 60 * 60)
    df_stats['hrPlayedAvg'] = df_stats['hrPlayed'] / df_stats['dayCount'].apply(lambda x: max(x, 1))
    df_stats['noStreamsAvg'] = df_stats['endTime'] / df_stats['dayCount'].apply(lambda x: max(x, 1))
    df_stats['lenStreamsAvgMin'] = df_stats['msPlayed'] / df_stats['endTime'].apply(lambda x: max(x, 1)) / (1000 * 60)
    
    result = []
    for day in days_order:
        day_data = df_stats[df_stats['weekday'] == day]
        if len(day_data) > 0:
            row = day_data.iloc[0]
            result.append({
                "weekday": day,
                "hrPlayedAvg": round(row['hrPlayedAvg'], 2),
                "noStreamsAvg": round(row['noStreamsAvg'], 1),
                "lenStreamsAvgMin": round(row['lenStreamsAvgMin'], 1)
            })
    
    return result

def analyze_listening_data(df: pd.DataFrame, start_date: str = None, end_date: str = None) -> Dict:
    """Main analysis function - returns complete analysis result"""
    df = df.copy()
    df['endTime'] = pd.to_datetime(df['endTime'])
    
    # Apply date filter if provided
    if start_date:
        df = df[df['endTime'] >= start_date]
    if end_date:
        df = df[df['endTime'] <= end_date]
    
    total_hours = df['msPlayed'].sum() / (1000 * 60 * 60)
    total_streams = len(df)
    
    return {
        "listening_over_time": load_over_time(df),
        "top_artists": get_top_artists(df),
        "top_tracks": get_top_tracks(df),
        "weekday_stats": get_weekday_stats(df),
        "total_hours": round(total_hours, 2),
        "total_streams": total_streams
    }
```

- [ ] **Step 3: Add analysis endpoint to main.py**

```python
# Add to imports
from analysis import analyze_listening_data, normalize_spotify_data
from schemas import AnalysisResult

@app.post("/analyze")
def analyze_tracks(tracks: List[Dict], start_date: str = None, end_date: str = None):
    """Analyze listening data and return stats"""
    df = normalize_spotify_data(tracks)
    result = analyze_listening_data(df, start_date, end_date)
    return result
```

- [ ] **Step 4: Test analysis endpoint**

```bash
# Create test file test_analysis.py
cd backend
```

```python
# test_analysis.py
import pandas as pd
from analysis import normalize_spotify_data, analyze_listening_data

# Test with sample data
sample_tracks = [
    {
        "track": {
            "artists": [{"name": "Taylor Swift"}],
            "name": "Love Story",
            "duration_ms": 233933
        },
        "played_at": "2024-01-15T10:30:00Z"
    }
]

df = normalize_spotify_data(sample_tracks)
print(f"Columns: {df.columns.tolist()}")
print(f"Artist: {df['artistName'].iloc[0]}")
```

```bash
python test_analysis.py
```
Expected: Prints `Columns: ['track', 'played_at', 'artistName', 'trackName', 'msPlayed', 'endTime']` and `Artist: Taylor Swift`

- [ ] **Step 5: Clean up test file and commit**

```bash
rm test_analysis.py
git add backend/
git commit -m "feat: port analysis functions from Python script"
```

---

### Task 4: Spotify API - Fetch Recently Played Tracks

**Files:**
- Create: `backend/spotify_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create spotify_api.py**

```python
import spotipy
from typing import List, Dict, Optional
from datetime import datetime, timedelta

def get_recently_played(sp: spotipy.Spotify, limit: int = 50, after: str = None) -> List[Dict]:
    """Fetch recently played tracks from Spotify API"""
    results = sp.current_user_recently_played(limit=limit, after=after)
    return results.get('items', [])

def get_top_artists(sp: spotipy.Spotify, time_range: str = 'medium_term', limit: int = 50) -> List[Dict]:
    """Fetch user's top artists"""
    results = sp.current_user_top_artists(limit=limit, time_range=time_range)
    return results.get('items', [])

def get_top_tracks(sp: spotipy.Spotify, time_range: str = 'medium_term', limit: int = 50) -> List[Dict]:
    """Fetch user's top tracks"""
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    return results.get('items', [])

def get_all_recently_played(sp: spotipy.Spotify, hours: int = 24) -> List[Dict]:
    """Fetch all recently played tracks within time window"""
    all_items = []
    after = None
    cutoff = datetime.now() - timedelta(hours=hours)
    
    while True:
        items = get_recently_played(sp, limit=50, after=after)
        if not items:
            break
        
        all_items.extend(items)
        
        # Check if we've gone back far enough
        oldest_item = items[-1]
        played_at = datetime.fromisoformat(oldest_item['played_at'].replace('Z', '+00:00'))
        if played_at < cutoff:
            break
        
        # Get timestamp for next page
        after = int(played_at.timestamp() * 1000)
        
        # Safety limit
        if len(all_items) >= 1000:
            break
    
    return all_items
```

- [ ] **Step 2: Add API endpoints to main.py**

```python
# Add to imports
from spotify_api import get_all_recently_played, get_top_artists, get_top_tracks
from spotify_auth import get_spotify_client

@app.get("/api/recently-played")
def recently_played(session_id: str, hours: int = 24, db: Session = next(get_db())):
    """Fetch user's recently played tracks"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}, 404
    
    sp = get_spotify_client(session.access_token)
    tracks = get_all_recently_played(sp, hours)
    
    return {"tracks": tracks, "count": len(tracks)}

@app.get("/api/top-artists")
def top_artists(session_id: str, time_range: str = "medium_term", db: Session = next(get_db())):
    """Fetch user's top artists"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}, 404
    
    sp = get_spotify_client(session.access_token)
    artists = get_top_artists(sp, time_range)
    
    return {"artists": artists}

@app.get("/api/top-tracks")
def top_tracks_api(session_id: str, time_range: str = "medium_term", db: Session = next(get_db())):
    """Fetch user's top tracks"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}, 404
    
    sp = get_spotify_client(session.access_token)
    tracks = get_top_tracks(sp, time_range)
    
    return {"tracks": tracks}
```

- [ ] **Step 3: Test with valid session**

```bash
# After OAuth flow, use the session_id from callback
curl "http://localhost:8000/api/recently-played?session_id=YOUR_SESSION_ID&hours=24"
```
Expected: Returns `{"tracks": [...], "count": N}`

- [ ] **Step 4: Commit**

```bash
git add backend/
git commit -m "feat: add Spotify API endpoints for recently played and top items"
```

---

### Task 5: JSON Upload Handler

**Files:**
- Create: `backend/upload.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create upload.py**

```python
import json
from typing import List, Dict
from analysis import normalize_spotify_data, analyze_listening_data

def parse_uploaded_json(file_content: str) -> List[Dict]:
    """Parse uploaded Spotify JSON file"""
    data = json.loads(file_content)
    
    # Handle both array and object with items
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'items' in data:
        return data['items']
    else:
        raise ValueError("Invalid Spotify data format")

def analyze_uploaded_data(file_contents: List[str], start_date: str = None, end_date: str = None) -> Dict:
    """Analyze multiple uploaded JSON files"""
    all_tracks = []
    
    for content in file_contents:
        tracks = parse_uploaded_json(content)
        all_tracks.extend(tracks)
    
    df = normalize_spotify_data(all_tracks)
    return analyze_listening_data(df, start_date, end_date)
```

- [ ] **Step 2: Add upload endpoint to main.py**

```python
# Add to imports
from upload import analyze_uploaded_data
from fastapi import UploadFile, File, Form

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
```

- [ ] **Step 3: Test upload endpoint**

```bash
# Create test file
echo '[{"ts":"2024-01-15T10:30:00Z","ms_played":233933,"master_metadata_track_name":"Test Song","master_metadata_album_artist_name":"Test Artist"}]' > test_upload.json

curl -X POST http://localhost:8000/upload \
  -F "files=@test_upload.json"
```
Expected: Returns analysis result with the test track

- [ ] **Step 4: Clean up and commit**

```bash
rm test_upload.json
git add backend/
git commit -m "feat: add JSON file upload and analysis endpoint"
```

---

### Task 6: Frontend Setup - Next.js Application

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/next.config.js`

- [ ] **Step 1: Initialize Next.js project**

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*" --eslint
```
Expected: Project created successfully

- [ ] **Step 2: Install additional dependencies**

```bash
cd frontend
npm install recharts lucide-react clsx tailwind-merge
```

- [ ] **Step 3: Update package.json scripts**

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

- [ ] **Step 4: Create landing page in app/page.tsx**

```typescript
export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-green-900 to-black text-white">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-6xl font-bold mb-4">Spotify Activity Analyzer</h1>
        <p className="text-2xl mb-8 text-gray-300">
          Discover your listening habits. Share your story.
        </p>
        
        <button 
          onClick={handleLogin}
          className="bg-green-500 hover:bg-green-600 text-black font-bold py-4 px-8 rounded-full text-lg transition"
        >
          Connect with Spotify
        </button>
        
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon="📊"
            title="Analyze Your Stats"
            description="See your top artists, tracks, and listening patterns"
          />
          <FeatureCard 
            icon="📅"
            title="Choose Any Date Range"
            description="Not just year-end - analyze any period you want"
          />
          <FeatureCard 
            icon="📱"
            title="Share on Social"
            description="Create beautiful cards to share on Instagram, Twitter"
          />
        </div>
      </div>
    </main>
  );

  function handleLogin() {
    window.location.href = 'http://localhost:8000/auth/login';
  }
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white/10 backdrop-blur rounded-xl p-6">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-300">{description}</p>
    </div>
  );
}
```

- [ ] **Step 5: Update app/layout.tsx**

```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Spotify Activity Analyzer',
  description: 'Analyze your Spotify listening habits and share your story',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

- [ ] **Step 6: Test frontend**

```bash
cd frontend
npm run dev
```
Expected: Server runs at http://localhost:3000, landing page displays

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: set up Next.js frontend with landing page"
```

---

### Task 7: Dashboard Page with Charts

**Files:**
- Create: `frontend/app/dashboard/page.tsx`
- Create: `frontend/components/charts/ListeningOverTimeChart.tsx`
- Create: `frontend/components/charts/TopArtistsChart.tsx`
- Create: `frontend/components/charts/WeekdayChart.tsx`
- Create: `frontend/components/DateRangePicker.tsx`

- [ ] **Step 1: Create DateRangePicker component**

```typescript
'use client';

import { useState } from 'react';

interface DateRangePickerProps {
  onApply: (start: string, end: string) => void;
}

export default function DateRangePicker({ onApply }: DateRangePickerProps) {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [preset, setPreset] = useState('');

  const applyPreset = (range: string) => {
    const now = new Date();
    let start: Date;

    switch (range) {
      case '7d':
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        start = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      default:
        return;
    }

    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(now.toISOString().split('T')[0]);
    setPreset(range);
  };

  const handleApply = () => {
    onApply(startDate, endDate);
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <h3 className="text-lg font-semibold mb-3">Select Date Range</h3>
      
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => applyPreset('7d')}
          className={`px-3 py-1 rounded ${preset === '7d' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}
        >
          Last 7 days
        </button>
        <button
          onClick={() => applyPreset('30d')}
          className={`px-3 py-1 rounded ${preset === '30d' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}
        >
          Last 30 days
        </button>
        <button
          onClick={() => applyPreset('90d')}
          className={`px-3 py-1 rounded ${preset === '90d' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}
        >
          Last 90 days
        </button>
      </div>

      <div className="flex gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="border rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="border rounded px-3 py-2"
          />
        </div>
        <button
          onClick={handleApply}
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
        >
          Apply
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create ListeningOverTimeChart component**

```typescript
'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DataPoint {
  date: string;
  hours: number;
}

export default function ListeningOverTimeChart({ data }: { data: DataPoint[] }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Listening Time Over Days</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis label={{ value: 'Hours', angle: -90 }} />
          <Tooltip />
          <Line type="monotone" dataKey="hours" stroke="#22c55e" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

- [ ] **Step 3: Create TopArtistsChart component**

```typescript
'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Artist {
  artistName: string;
  noStreams: number;
  streamTimeHr: number;
}

export default function TopArtistsChart({ data }: { data: Artist[] }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Top Artists</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="artistName" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" />
          <YAxis yAxisId="left" orientation="left" stroke="#ef4444" />
          <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" />
          <Tooltip />
          <Legend />
          <Bar yAxisId="left" dataKey="noStreams" fill="#ef4444" name="Streams" />
          <Bar yAxisId="right" dataKey="streamTimeHr" fill="#3b82f6" name="Hours" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

- [ ] **Step 4: Create WeekdayChart component**

```typescript
'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface WeekdayStat {
  weekday: string;
  hrPlayedAvg: number;
  noStreamsAvg: number;
}

export default function WeekdayChart({ data }: { data: WeekdayStat[] }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Listening by Day of Week</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="weekday" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="hrPlayedAvg" fill="#22c55e" name="Avg Hours" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

- [ ] **Step 5: Create dashboard page**

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import DateRangePicker from '@/components/DateRangePicker';
import ListeningOverTimeChart from '@/components/charts/ListeningOverTimeChart';
import TopArtistsChart from '@/components/charts/TopArtistsChart';
import WeekdayChart from '@/components/charts/WeekdayChart';

interface AnalysisData {
  listening_over_time: { date: string; hours: number }[];
  top_artists: { artistName: string; noStreams: number; streamTimeHr: number }[];
  top_tracks: { artistName: string; trackName: string; noStreams: number; streamTimeHr: number }[];
  weekday_stats: { weekday: string; hrPlayedAvg: number }[];
  total_hours: number;
  total_streams: number;
}

export default function Dashboard() {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (sessionId) {
      fetchAnalysis(sessionId);
    }
  }, [sessionId]);

  const fetchAnalysis = async (session: string, start?: string, end?: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/recently-played?session_id=${session}&hours=720`);
      const tracksData = await res.json();
      
      const analyzeRes = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tracksData.tracks, start, end),
      });
      const result = await analyzeRes.json();
      setData(result);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  if (!sessionId) {
    return <div className="p-8">Please connect Spotify first</div>;
  }

  if (loading) {
    return <div className="p-8">Loading your stats...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Your Spotify Stats</h1>
        
        <div className="grid grid-cols-3 gap-4 mb-6">
          <StatCard label="Total Listening Time" value={`${data?.total_hours || 0} hours`} />
          <StatCard label="Total Streams" value={`${data?.total_streams || 0} tracks`} />
          <StatCard label="Top Artist" value={data?.top_artists?.[0]?.artistName || '-'} />
        </div>

        <DateRangePicker onApply={(start, end) => fetchAnalysis(sessionId, start, end)} />

        <div className="grid md:grid-cols-2 gap-6">
          {data?.listening_over_time && <ListeningOverTimeChart data={data.listening_over_time} />}
          {data?.top_artists && <TopArtistsChart data={data.top_artists} />}
          {data?.weekday_stats && <WeekdayChart data={data.weekday_stats} />}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}
```

- [ ] **Step 6: Test dashboard**

```bash
cd frontend
npm run dev
# Visit http://localhost:3000/dashboard?session_id=YOUR_SESSION_ID
```

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: create dashboard with interactive charts"
```

---

### Task 8: Social Sharing Cards

**Files:**
- Create: `frontend/components/ShareableCard.tsx`
- Create: `frontend/lib/export.ts`
- Create: `frontend/app/share/page.tsx`

- [ ] **Step 1: Create export utility**

```typescript
import html2canvas from 'html2canvas';

export async function downloadAsPNG(elementId: string, filename: string = 'spotify-stats.png') {
  const element = document.getElementById(elementId);
  if (!element) return;

  const canvas = await html2canvas(element, {
    scale: 2,
    backgroundColor: '#1a1a2e',
  });

  const blob = canvas.toDataURL('image/png');
  const link = document.createElement('a');
  link.download = filename;
  link.href = blob;
  link.click();
}

export async function shareToTwitter(imageBlob: string, text: string) {
  // Twitter doesn't support direct image upload via web intent
  // Download first, then user can manually upload
  const tweetText = encodeURIComponent(text);
  window.open(`https://twitter.com/intent/tweet?text=${tweetText}`, '_blank');
}
```

- [ ] **Step 2: Install html2canvas**

```bash
cd frontend
npm install html2canvas
```

- [ ] **Step 3: Create ShareableCard component**

```typescript
'use client';

interface ShareableCardProps {
  title: string;
  subtitle: string;
  mainStat: string;
  accentColor?: string;
  gradient?: [string, string];
}

export default function ShareableCard({
  title,
  subtitle,
  mainStat,
  accentColor = '#1db954',
  gradient = ['#1a1a2e', '#16213e'],
}: ShareableCardProps) {
  return (
    <div
      id="share-card"
      className="w-[540px] h-[960px] p-8 rounded-2xl shadow-2xl"
      style={{
        background: `linear-gradient(135deg, ${gradient[0]}, ${gradient[1]})`,
      }}
    >
      <div className="flex items-center gap-4 mb-8">
        <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center">
          <svg className="w-10 h-10 text-black" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
          </svg>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Spotify Activity Analyzer</h2>
          <p className="text-gray-400">{subtitle}</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center items-center">
        <div className="text-6xl font-bold text-white mb-4">{mainStat}</div>
        <div className="text-2xl text-gray-300">{title}</div>
      </div>

      <div className="mt-auto pt-8 border-t border-white/20">
        <p className="text-gray-400 text-center">Made with Spotify Activity Analyzer</p>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create share page**

```typescript
'use client';

import { useState } from 'react';
import ShareableCard from '@/components/ShareableCard';
import { downloadAsPNG } from '@/lib/export';

export default function SharePage() {
  const [cardData, setCardData] = useState({
    title: 'Top Artist',
    subtitle: 'Last 30 days',
    mainStat: 'Taylor Swift',
  });

  const handleDownload = () => {
    downloadAsPNG('share-card', 'my-spotify-stats.png');
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">Share Your Stats</h1>
        
        <div className="flex gap-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-white font-semibold mb-4">Customize Card</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm">Title</label>
                <input
                  type="text"
                  value={cardData.title}
                  onChange={(e) => setCardData({ ...cardData, title: e.target.value })}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm">Subtitle</label>
                <input
                  type="text"
                  value={cardData.subtitle}
                  onChange={(e) => setCardData({ ...cardData, subtitle: e.target.value })}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm">Main Stat</label>
                <input
                  type="text"
                  value={cardData.mainStat}
                  onChange={(e) => setCardData({ ...cardData, mainStat: e.target.value })}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                />
              </div>
            </div>

            <button
              onClick={handleDownload}
              className="mt-6 w-full bg-green-500 hover:bg-green-600 text-black font-bold py-3 rounded-lg"
            >
              Download as PNG
            </button>
          </div>

          <div>
            <ShareableCard
              title={cardData.title}
              subtitle={cardData.subtitle}
              mainStat={cardData.mainStat}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Test share functionality**

```bash
cd frontend
npm run dev
# Visit http://localhost:3000/share
# Click "Download as PNG" and verify image downloads
```

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: add shareable cards with PNG export"
```

---

### Task 9: Deployment Setup

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`
- Create: `README.md`

- [ ] **Step 1: Create backend Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create frontend Dockerfile**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
      - SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET}
      - SPOTIFY_REDIRECT_URI=${SPOTIFY_REDIRECT_URI}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/spotify
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=spotify
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

- [ ] **Step 4: Create deployment README**

```markdown
# Deployment Guide

## Local Development

```bash
# Set environment variables
cp backend/.env.example backend/.env
# Edit with your Spotify credentials

# Run with Docker
docker-compose up

# Or run separately
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

## Deploy to Railway (Backend)

1. Install Railway CLI: `npm i -g @railway/cli`
2. `railway login`
3. `railway init` in backend folder
4. Add environment variables in Railway dashboard
5. `railway up`

## Deploy to Vercel (Frontend)

1. Install Vercel CLI: `npm i -g vercel`
2. `vercel login`
3. `vercel` in frontend folder
4. Add environment variables in Vercel dashboard
```

- [ ] **Step 5: Test Docker setup**

```bash
docker-compose up --build
```
Expected: Both services start, visit http://localhost:3000

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile README.md
git commit -m "feat: add Docker deployment configuration"
```

---

## Timeline Summary

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1-2 | Backend Foundation | OAuth, API integration, analysis endpoints |
| 3-4 | Frontend Core | Landing page, dashboard, charts |
| 5-6 | Social Features | Shareable cards, PNG export |
| 7-8 | Polish & Deploy | Bug fixes, deployment, documentation |

---

## Next Steps

1. **Get Spotify Developer Credentials**: Visit https://developer.spotify.com/dashboard, create app, get Client ID & Secret
2. **Start with Task 1**: Run through backend setup
3. **Ask questions early**: If stuck on OAuth or any step, ask before spending hours

Ready to begin? I can execute this plan task-by-task using subagent-driven-development, or you can work through it manually.
