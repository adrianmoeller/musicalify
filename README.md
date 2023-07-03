# Musicalify

A Spotify application that shows detailed musical information about songs.

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
      - `SPOTIPY_REDIRECT_URI`
   - Linux: `export <name>=<value>`
   - Windows: `set <name>=<value>`
8. Run the server
   - Linux: `python3 main.py`
   - Windows: `python main.py`
10. To access the web-app, open `http://127.0.0.1:8050/` in your preferred browser
