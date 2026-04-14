 Spotify Activity Analyzer - Project Status

**Last Updated:** 2026-04-13  
**Plan Reference:** `docs/buzzing-swimming-widget.md`

---

## Completed Tasks

### Task 1: Project Setup - Backend Foundation ✅

**Files Created:**
- `backend/requirements.txt` - Python dependencies (updated for Python 3.13 compatibility)
- `backend/config.py` - Environment configuration
- `backend/.env` - Spotify OAuth credentials
- `backend/.env.example` - Template for credentials
- `backend/.gitignore` - Protects secrets and build artifacts
- `backend/main.py` - FastAPI application entry point

**Dependencies Installed:**
- fastapi >= 0.109.0
- uvicorn[standard] >= 0.27.0
- python-dotenv >= 1.0.0
- spotipy >= 2.23.0
- pandas >= 2.2.0
- sqlalchemy >= 2.0.25
- alembic >= 1.13.1

**Issues Faced:**
1. **pandas==2.1.4 build failure** - Pinned version required building from source with GCC >= 8.4, but system has GCC 6.3.0. Fixed by changing to `pandas>=2.2.0` which has pre-built wheels for Python 3.13.
2. **uvicorn==0.27.0 dependency issues** - Same issue, fixed by using flexible version constraints.

---

### Task 2: Spotify OAuth Authentication ✅

**Files Created:**
- `backend/models.py` - SQLAlchemy database models (UserSession)
- `backend/spotify_auth.py` - OAuth helper functions
- `backend/spotify_analyzer.db` - SQLite database (auto-created)

**Endpoints Implemented:**
- `GET /auth/login` - Returns Spotify OAuth authorization URL
- `GET /callback` - Handles OAuth callback, exchanges code for tokens, creates session

**Issues Faced:**
1. **Spotify redirect URI** - `localhost` wasn't accepted in Spotify Dashboard. Fixed by using `127.0.0.1` instead.
2. **spotipy `cache_file` parameter deprecated** - Removed `cache_file=None` from SpotifyOAuth init.
3. **FastAPI `Depends` syntax** - Initial code used `next(get_db())` instead of `Depends(get_db())`. Fixed for all endpoints.

---

### Task 3: Data Analysis Module ✅

**Files Created:**
- `backend/schemas.py` - Pydantic schemas for API responses
- `backend/analysis.py` - Ported analysis functions from original Python script
- `backend/spotify_api.py` - Spotify API wrapper functions

**Endpoints Implemented:**
- `POST /analyze` - Analyze track data and return stats
- `GET /api/recently-played` - Fetch user's recently played tracks
- `GET /api/top-artists` - Fetch user's top artists
- `GET /api/top-tracks` - Fetch user's top tracks

**Functions Ported from Original Script:**
- `ms2hr()` - Milliseconds to hours conversion
- `normalize_spotify_data()` - Normalize Spotify API/uploaded JSON data
- `load_over_time()` - Listening time per day
- `get_top_artists()` - Top artists by stream count
- `get_top_tracks()` - Top tracks by stream count
- `get_weekday_stats()` - Streaming patterns by day of week
- `analyze_listening_data()` - Main analysis function

**Issues Faced:**
1. **Wrong imports in main.py** - File was modified with `narwhals.List` and `pyparsing.Dict` instead of `typing.List` and `typing.Dict`. Fixed.

---

## Pending Tasks

### Task 4: Frontend Implementation (Not Started)

**Files to Create:**
- `frontend/package.json` - Next.js project setup
- `frontend/app/page.tsx` - Landing page with OAuth login
- `frontend/app/dashboard/page.tsx` - Analysis dashboard
- `frontend/components/DateRangePicker.tsx`
- `frontend/components/StatsCard.tsx`
- `frontend/components/charts/*.tsx`
- `frontend/lib/spotify.ts`
- `frontend/lib/export.ts` - PNG export for social sharing

### Task 5: Social Sharing Features (Not Started)

**Features:**
- "Wrapped-style" percentage metrics
- Shareable cards (1080x1920 for Instagram Stories)
- PNG export via html2canvas
- Direct Twitter sharing

### Task 6: Polish & Deployment (Not Started)

**Tasks:**
- User profiles (public/private toggle)
- Shareable links
- Dark mode
- Production deployment (Vercel + Railway/Render)

---

## How to Resume Development

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

Server will run at: `http://127.0.0.1:8000`

### Test OAuth Flow

1. Visit `http://127.0.0.1:8000/auth/login` to get auth URL
2. Click the URL and authorize with Spotify
3. After redirect to `/callback?code=...`, you'll receive a `session_id`
4. Use `session_id` with `/api/recently-played`, `/api/top-artists`, `/api/top-tracks`

### Test Analysis Endpoint

```python
import requests

tracks = [{
    "track": {
        "artists": [{"name": "Artist Name"}],
        "name": "Track Name",
        "duration_ms": 200000
    },
    "played_at": "2024-01-15T10:30:00Z"
}]

resp = requests.post("http://127.0.0.1:8000/analyze", json=tracks)
print(resp.json())
```

---

## Session Continuation Prompt

```
Continue development of the Spotify Activity Analyzer web application.

**Context:**
- Backend foundation (Tasks 1-3) is complete and working
- FastAPI server running at http://127.0.0.1:8000
- OAuth flow functional - users can authenticate with Spotify
- Analysis endpoints working - returns listening stats as JSON
- Database: SQLite at backend/spotify_analyzer.db

**Next Steps (choose one):**
1. Start Task 4 - Build Next.js frontend with dashboard
2. Add more analysis features (genre breakdown, artist consistency score)
3. Implement frontend for OAuth + data visualization
4. Set up database migrations with Alembic

**Plan Reference:** docs/buzzing-swimming-widget.md

**Known Issues to Watch:**
- All FastAPI endpoints using database must use `Depends(get_db())` not `next(get_db())`
- Use flexible version constraints in requirements.txt for Python 3.13 compatibility
- Spotify redirect URI must be `http://127.0.0.1:8000/callback` (not localhost)
```

---

## File Structure

```
Spotify Activity Analyzer/
├── backend/
│   ├── .env                    # Spotify credentials (DO NOT COMMIT)
│   ├── .env.example            # Template
│   ├── .gitignore              # Git ignore rules
│   ├── requirements.txt        # Dependencies
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Environment config
│   ├── models.py               # SQLAlchemy models
│   ├── spotify_auth.py         # OAuth helpers
│   ├── spotify_api.py          # Spotify API wrappers
│   ├── analysis.py             # Data analysis functions
│   ├── schemas.py              # Pydantic schemas
│   └── spotify_analyzer.db     # SQLite database
├── docs/
│   └── buzzing-swimming-widget.md  # Implementation plan
├── spotify_activity_analyzer.py    # Original CLI script
├── CLAUDE.md                       # Project instructions
└── PROJECT_STATUS.md               # This file
```

---

## Git Status

**Uncommitted Changes:** Backend files for Tasks 1-3 need to be committed.

**Recommended Commit Message:**
```
feat: implement backend API with OAuth and analysis endpoints

- FastAPI server with CORS middleware
- Spotify OAuth authentication flow
- Data analysis endpoints (top artists, tracks, weekday stats)
- SQLite database for session storage
```
