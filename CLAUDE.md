# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spotify Activity Analyzer - A Python script that analyzes Spotify streaming history JSON files and generates visualizations for listening patterns.

## Running the Analyzer

```bash
python spotify_activity_analyzer.py
```

The script expects JSON streaming history files in a subdirectory called `Spotify Extended Streaming History/` with filenames starting with `Streaming_History_`.

## Dependencies

- pandas - data manipulation
- matplotlib - plotting
- seaborn - visualization styling
- numpy - numerical operations

Install with: `pip install pandas matplotlib seaborn numpy`

## Code Structure

All code is in `spotify_activity_analyzer.py`. Key functions:

- `file2df()` - Loads and combines multiple JSON streaming history files
- `choose_date_range()` - Interactive menu for filtering data by date
- `load_over_time()` - Calculates total listening time per day
- `avg_day_load()` - Analyzes streaming patterns by day of week
- `top_artists()` / `top_tracks()` - Top content by streams and play time
- `top_artists_history()` - Streaming history trends for top artists
- `top_artists_most_days()` - Artists listened to on most unique days
- `plot_df()` - Generic bar chart plotting utility
- `ms2hr()` - Milliseconds to hours conversion

## Data Format

Expects Spotify Extended Streaming History JSON format with fields:
- `ts` - timestamp (milliseconds)
- `master_metadata_album_artist_name` - artist
- `master_metadata_track_name` - track name
- `ms_played` - play duration in milliseconds
