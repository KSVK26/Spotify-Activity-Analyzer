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