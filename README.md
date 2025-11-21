# 🔥 Music Sync - Universal Music Platform Synchronizer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

A beautiful, production-ready web application for seamlessly syncing playlists between music streaming platforms. Currently supports **Spotify ↔ YouTube Music** with a roadmap for Apple Music, Amazon Music, and Tidal.

**Live Demo:** [https://mymusicsync.duckdns.org](https://mymusicsync.duckdns.org)

## ✨ Features

- 🎵 **Bidirectional Sync**: Transfer playlists from Spotify → YouTube Music or YouTube Music → Spotify
- 👥 **Multi-User Support**: Secure authentication system with encrypted credentials
- 📊 **Real-Time Progress**: Live sync progress with Server-Sent Events (SSE)
- 📝 **Sync History**: Track all your playlist transfers with timestamps
- 🎨 **Premium UI**: Beautiful "On Fire" color palette with smooth animations
- 🔐 **Secure OAuth**: Industry-standard OAuth 2.0 for Spotify authentication
- 🐳 **Docker Ready**: One-command deployment with Docker Compose
- 🔒 **HTTPS/SSL**: Production-ready with Let's Encrypt certificates
- 💾 **Backup System**: Automated database backups

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Spotify Developer Account
- YouTube Music account (with uploaded music library)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/spotify_to_ytmusic.git
cd spotify_to_ytmusic
```

2. **Install dependencies**
```bash
pip install -r requirements-web.txt
```

3. **Configure environment**
```bash
cp .env.example .env
nano .env
```

Add your credentials:
```env
SECRET_KEY=your_secret_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

4. **Run the application**
```bash
python3 app.py
```

Visit `http://localhost:5000` in your browser!

## 🐳 Docker Deployment

### Quick Deploy (HTTP)

```bash
docker-compose up -d
```

### Production Deploy (HTTPS with SSL)

1. **Set up your domain** (using Duck DNS or your own domain)
```bash
# Update your domain's A record to point to your server IP
```

2. **Run the SSL setup script**
```bash
chmod +x setup-ssl.sh
./setup-ssl.sh
```

3. **Update environment variables**
```bash
nano .env
# Add your Spotify credentials
```

4. **Deploy**
```bash
docker-compose up -d --build
```

Your app will be live at `https://yourdomain.com`!

## 📋 Detailed Setup Guides

### Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Note your `Client ID` and `Client Secret`
4. Add redirect URI: `https://yourdomain.com/spotify/callback`
5. Add these to your `.env` file

### YouTube Music Setup

1. Install [ytmusicapi](https://github.com/sigma67/ytmusicapi) locally:
```bash
pip install ytmusicapi
ytmusicapi oauth
```

2. This creates `oauth.json` with your YouTube Music credentials
3. In the web app, go to Settings → YouTube Music → Upload Headers
4. Upload your `oauth.json` file

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.0, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **APIs**: Spotify Web API, YouTube Music API (ytmusicapi)
- **Database**: SQLite (easily swappable to PostgreSQL)
- **Deployment**: Docker, Docker Compose, Nginx, Let's Encrypt
- **Security**: Bcrypt password hashing, OAuth 2.0, HTTPS/TLS 1.3

## 📸 Screenshots

> Coming soon! Feel free to contribute screenshots in the Issues or Pull Requests.

## 🗺️ Roadmap

### Current Platforms
- ✅ Spotify
- ✅ YouTube Music

### Planned Integrations
- 🎵 **Apple Music** - Waiting for better API access
- 🎶 **Amazon Music** - Awaiting API improvements
- 🌊 **Tidal** - Coming to India soon!
- 🎧 **Deezer** - Under consideration
- ☁️ **SoundCloud** - Under consideration

### Feature Roadmap
- [ ] Playlist scheduling (auto-sync daily/weekly)
- [ ] Liked songs sync
- [ ] Album sync
- [ ] Smart playlist matching (fuzzy matching for missing songs)
- [ ] Sync statistics and analytics
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] CLI tool improvements

## 🤝 Contributing

Contributions are **highly encouraged**! Whether you want to:
- Add support for new music platforms
- Improve the UI/UX
- Fix bugs or improve performance
- Add new features
- Improve documentation

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) by sigma67 - Excellent YouTube Music API wrapper
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - Comprehensive music platform API
- [Flask](https://flask.palletsprojects.com/) - Lightweight and powerful web framework

## 🐛 Known Issues

- YouTube Music search may not find exact matches for some songs (API limitation)
- Spotify rate limiting may slow down large playlist syncs (>1000 songs)
- Some regional restrictions may apply based on music availability

## 💬 Support

- 📧 **Email**: Open an issue on GitHub
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/spotify_to_ytmusic/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/spotify_to_ytmusic/discussions)

## ⭐ Star History

If you find this project useful, please consider giving it a star! It helps others discover the project.

---

## 📚 Legacy CLI Tool

This repository also contains the original command-line tool for migrating playlists. See below for CLI instructions.

<details>
<summary><strong>Click to expand CLI documentation</strong></summary>

#### 2. Generate YouTube Music Credentials

To use the YouTube Music API, you need to generate valid credentials. Follow these steps:

1. **Log in to YouTube Music**: Open YouTube Music in Firefox and ensure you are logged in.
2. **Open the Inspection Tool**: Press `F12` or right-click and select _Inspect_ to open the browser's inspection tool.
3. **Access the Network Tab**: Navigate to the Network tab and filter by `/browse`.
4. **Select a Request**: Click one of the requests under the filtered results and locate the _Request Headers_ section.
5. **Toggle RAW View**: Click the RAW toggle button to view the headers in raw format.
6. **Copy Headers**: Right-click, choose _Select All_, and copy the content.
7. **Paste into `raw_headers.txt`**: Open the `raw_headers.txt` file located in the main directory of this project and paste the copied content into it.

**Run the Script**:

Execute the following command to generate the credentials file:

On Windows:

```bash
python spotify2ytmusic/ytmusic_credentials.py
```

On Linux or Mac:

```bash
python3 spotify2ytmusic/ytmusic_credentials.py
```

**Important**: After running this script, the authentication file will be created.
When you launch the GUI in the next step, it will automatically detect this file and log in to YouTube Music without requiring manual input. You’ll see a log message confirming this:

```
File detected, auto login
```

The GUI will **ignore the 'Login to YT Music' tab** and jump straight to the 'Spotify Backup' tab.

---

#### 3. Use the GUI for Migration

Now you can use the graphical user interface (GUI) to migrate your playlists and liked songs to YouTube Music. Start the GUI with the following command:

On Windows:

```bash
python -m spotify2ytmusic gui
```

On Linux or Mac:

```bash
python3 -m spotify2ytmusic gui
```

---

### GUI Features

Once the GUI is running, you can:

- **Backup Your Spotify Playlists**: Save your playlists and liked songs into the file `playlists.json`.
- **Load Liked Songs**: Migrate your Spotify liked songs to YouTube Music.
- **List Playlists**: View your playlists and their details.
- **Copy All Playlists**: Migrate all Spotify playlists to YouTube Music.
- **Copy a Specific Playlist**: Select and migrate a specific Spotify playlist to YouTube Music.

---

### Import Your Liked Songs - Tab 3

#### Click the `import` button, and wait until it finished and switched to the next tab

It will go through your Spotify liked songs, and like them on YTMusic. It will display
the song from Spotify and then the song that it found on YTMusic that it is liking. I've
spot-checked my songs and it seems to be doing a good job of matching YTMusic songs with
Spotify. So far I haven't seen a single failure across a couple hundred songs, but more
esoteric titles it may have issues with.

### List Your Playlists - Tab 4

#### Click the `list` button, and wait until it finished and switched to the next tab

This will list the playlists you have on both Spotify and YTMusic, so you can individually copy them.

### Copy Your Playlists - Tab 5

You can either copy **all** playlists, or do a more surgical copy of individual playlists.
Copying all playlists will use the name of the Spotify playlist as the destination playlist name on YTMusic.

#### To copy all the playlists click the `copy` button, and wait until it finished and switched to the next tab

**NOTE**: This does not copy the Liked playlist (see above to do that).

### Copy specific Playlist - Tab 6

In the list output, find the "playlist id" (the first column) of the Spotify playlist and of the YTMusic playlist.

#### Then fill both input fields and click the `copy` button

The copy playlist will take the name of the YTMusic playlist and will create the
playlist if it does not exist, if you start the YTMusic playlist with a "+":

Re-running "copy_playlist" or "load_liked" in the event that it fails should be safe, it
will not duplicate entries on the playlist.

## Command Line Usage

### Ways to Run

**NOTE**: There are two possible ways to run these commands, one is via standalone commands
if the application was installed, which takes the form of: `s2yt_load_liked`

If not fully installed, you can replace the "s2yt\_" with "python -m spotify2ytmusic", for
example: `s2yt_load_liked` becomes `python -j spotify2ytmusic load_liked`

### Login to YTMusic

See "Generate YouTube Music Credentials" above.

### Backup Your Spotify Playlists

Run `spotify2ytmusic/spotify_backup.py` and it will help you authorize access to your spotify account.

Run: `python3 spotify_backup.py playlists.json --dump=liked,playlists --format=json`

This will save your playlists and liked songs into the file "playlists.json".

### Import Your Liked Songs

Run: `s2yt_load_liked`

It will go through your Spotify liked songs, and like them on YTMusic. It will display
the song from spotify and then the song that it found on YTMusic that it is liking. I've
spot-checked my songs and it seems to be doing a good job of matching YTMusic songs with
Spotify. So far I haven't seen a single failure across a couple thousand songs, but more
esoteric titles it may have issues with.

### Import Your Liked Albums

Run: `s2yt_load_liked_albums`

Spotify stores liked albums outside of the "Liked Songs" playlist. This is the command to
load your liked albums into YTMusic liked songs.

### List Your Playlists

Run `s2yt_list_playlists`

This will list the playlists you have on both Spotify and YTMusic. You will need to
individually copy them.

### Copy Your Playlists

You can either copy **all** playlists, or do a more surgical copy of individual playlists.
Copying all playlists will use the name of the Spotify playlist as the destination
playlist name on YTMusic. To copy all playlists, run:

`s2yt_copy_all_playlists`

**NOTE**: This does not copy the Liked playlist (see above to do that).

In the list output above, find the "playlist id" (the first column) of the Spotify playlist,
and of the YTMusic playlist, and then run:

`s2yt_copy_playlist <SPOTIFY_PLAYLIST_ID> <YTMUSIC_PLAYLIST_ID>`

If you need to create a playlist, you can run:

`s2yt_create_playlist "<PLAYLIST_NAME>"`

_Or_ the copy playlist can take the name of the YTMusic playlist and will create the
playlist if it does not exist, if you start the YTMusic playlist with a "+":

`s2yt_copy_playlist <SPOTIFY_PLAYLIST_ID> +<YTMUSIC_PLAYLIST_NAME>`

For example:

`s2yt_copy_playlist SPOTIFY_PLAYLIST_ID "+Feeling Like a PUNK"`

Re-running "copy_playlist" or "load_liked" in the event that it fails should be safe, it
will not duplicate entries on the playlist.

### Searching for YTMusic Tracks

This is mostly for debugging, but there is a command to search for tracks in YTMusic:

## `s2yt_search --artist <ARTIST> --album <ALBUM> <TRACK_NAME>`

## Details About Search Algorithms

The function first searches for albums by the given artist name on YTMusic.

It then iterates over the first three album results and tries to find a track with
the exact same name as the given track name. If it finds a match, it returns the
track information.

If the function can't find the track in the albums, it then searches for songs by the
given track name and artist name.

Depending on the yt_search_algo parameter, it performs one of the following actions:

If yt_search_algo is 0, it simply returns the first song result.

If yt_search_algo is 1, it iterates over the song results and returns the first song
that matches the track name, artist name, and album name exactly. If it can't find a
match, it raises a ValueError.

If yt_search_algo is 2, it performs a fuzzy match. It removes everything in brackets
in the song title and checks for a match with the track name, artist name, and album
name. If it can't find a match, it then searches for videos with the track name and
artist name. If it still can't find a match, it raises a ValueError.

If the function can't find the track using any of the above methods, it raises a
ValueError.

## FAQ

- My copy is failing after 20-40 minutes. Is my session timing out?

Try playing music in the browser on Youtube Music while you are loading the playlists,
this has been reported to keep the session from timing out.

- Does this run on mobile?

No, this runs on Linux/Windows/MacOS.

- How does the lookup algorithm work?

  Given the Spotify track information, it does a lookup for the album by the same artist
  on YTMusic, then looks at the first 3 hits looking for a track with exactly the same
  name. In the event that it can't find that exact track, it then does a search of songs
  for the track name by the same artist and simply returns the first hit.

  The idea is that finding the album and artist and then looking for the exact track match
  will be more likely to be accurate than searching for the song and artist and relying on
  the YTMusic algorithm to figure things out, especially for short tracks that might be
  have many contradictory hits like "Survival by Yes".

- My copy is failing with repeated "ERROR: (Retrying) Server returned HTTP 400: Bad
  Request".

  Try running with "--track-sleep=3" argument to do a 3 second sleep between tracks. This
  will take much longer, but may succeed where faster rates have failed.

## License

Creative Commons Zero v1.0 Universal

spotify-backup.py licensed under MIT License.
See <https://github.com/caseychu/spotify-backup> for more information.

[//]: # " vim: set tw=90 ts=4 sw=4 ai: "
