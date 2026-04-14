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

