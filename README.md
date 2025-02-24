# Spotify to YouTube Playlist Converter

This script converts a Spotify playlist to a list of equivalent YouTube videos.

## Setup

1. Install UV (if not already installed):

```bash
curl -LsSf curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
uv pip install -r requirements.txt
```

## Usage

Run the script with a Spotify playlist URL:

```bash
python convert.py "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID"
```

The script will:

1. Open the Spotify playlist
2. Extract all track names
3. Search for each track on YouTube
4. Print a list of track names with their corresponding YouTube URLs
