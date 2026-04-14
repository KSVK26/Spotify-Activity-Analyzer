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