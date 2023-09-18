# Musicalify

A Spotify application that shows detailed musical information about songs.

### Features (so far):

- Drag and drop Spotify tracks, playlists, and albums to display detailed information
- Displayed information:
  - BPM
    - Sort by BPM
    - BPM filter
    - Half/double displayed BPM that exceeds/deceeds a given threshold
    - Manually correct a track's BPM value (stored offline)
    - Import/export stored BPM correction values
  - Musical features: acousticness, danceability, energy, instrumentalness, valence
- Select a track to display it in the Spotify app
- Add a track to the Spotify queue

## How to run:

1. Clone this repository with `git clone https://github.com/adrianmoeller/musicalify.git`
2. Navigate to the just cloned repository folder
3. (If you haven't already installed `virtualenv`, do it with `pip install virtualenv`)
4. Create a virtual environment with `virtualenv venv`
5. Activate the virtual environment
   - Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate.bat`
6. Install the requirements in the current environment with `pip install -r requirements.txt`
7. Set environment variables for Spotipy (take a look at the [Spotify Developer Documentation](https://developer.spotify.com/documentation/web-api/tutorials/getting-started), on how to get them)
   - Environment variables to set:
      - `SPOTIPY_CLIENT_ID`
      - `SPOTIPY_CLIENT_SECRET`
      - `SPOTIPY_REDIRECT_URI` (choose same URI as described in point 9.)
   - Linux: `export <name>=<value>`
   - Windows: `set <name>=<value>`
8. Run the server
   - Linux: `python3 main.py`
   - Windows: `python main.py`
9. To access the web-app, open `http://127.0.0.1:8050/` in your preferred browser
