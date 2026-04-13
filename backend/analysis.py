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