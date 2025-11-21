# Setup Documentation

This guide will walk you through setting up Music Sync from scratch, including obtaining API credentials from Spotify and YouTube Music.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Spotify API Setup](#spotify-api-setup)
3. [YouTube Music Setup](#youtube-music-setup)
4. [Environment Configuration](#environment-configuration)
5. [Database Initialization](#database-initialization)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

- **Python 3.9 or higher** installed
- **Git** installed
- A **Spotify account** (free or premium)
- A **YouTube Music account** with some music in your library
- A modern web browser (Chrome, Firefox, or Safari)

---

## Spotify API Setup

### Step 1: Create a Spotify Developer Account

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Accept the Terms of Service if prompted

### Step 2: Create an Application

1. Click **"Create app"**
2. Fill in the app details:
   - **App name**: `Music Sync` (or any name you prefer)
   - **App description**: `Personal playlist synchronization tool`
   - **Website**: Leave blank or use your domain
   - **Redirect URIs**: 
     - For local development: `http://localhost:5000/spotify/callback`
     - For production: `https://yourdomain.com/spotify/callback`
   - **APIs used**: Select "Web API"
3. Click **"Save"**

### Step 3: Get Your Credentials

1. On your app's dashboard, you'll see:
   - **Client ID**: Copy this
   - **Client Secret**: Click "View client secret" and copy it
2. Save these values - you'll need them for the `.env` file

### Step 4: Configure Redirect URIs

1. Click **"Edit Settings"**
2. Under **Redirect URIs**, make sure you have:
   - `http://localhost:5000/spotify/callback` (for development)
   - `https://yourdomain.com/spotify/callback` (for production)
3. Click **"Add"** then **"Save"**

> **Important**: The redirect URI must match exactly (including http/https and port)

---

## YouTube Music Setup

YouTube Music doesn't have an official OAuth flow like Spotify, so we use header-based authentication via `ytmusicapi`.

### Method 1: Using ytmusicapi OAuth (Recommended)

1. **Install ytmusicapi**:
```bash
pip install ytmusicapi
```

2. **Run the OAuth setup**:
```bash
ytmusicapi oauth
```

3. **Follow the prompts**:
   - A browser window will open
   - Log in to your Google account
   - Grant permissions to YouTube Music
   - The tool will create an `oauth.json` file

4. **Upload to Music Sync**:
   - Log in to Music Sync web app
   - Go to **Dashboard** → **YouTube Music** section
   - Click **"Upload Headers"**
   - Upload the `oauth.json` file

### Method 2: Manual Header Extraction (Alternative)

If the OAuth method doesn't work, you can manually extract headers:

1. **Open YouTube Music in Firefox**:
   - Go to [music.youtube.com](https://music.youtube.com)
   - Make sure you're logged in

2. **Open Developer Tools**:
   - Press `F12` or right-click → **Inspect**

3. **Navigate to Network Tab**:
   - Click the **Network** tab
   - Filter by `/browse`

4. **Capture a Request**:
   - Click on any song or playlist to trigger a request
   - Look for a request to `/browse` in the Network tab

5. **Copy Request Headers**:
   - Click on the request
   - Find **Request Headers** section
   - Click **Raw** to view raw headers
   - Right-click → **Select All** → **Copy**

6. **Save to File**:
   - Create a file called `raw_headers.txt`
   - Paste the copied headers

7. **Generate OAuth JSON**:
```bash
python3 spotify2ytmusic/ytmusic_credentials.py
```

8. **Upload to Music Sync**:
   - Upload the generated `oauth.json` file in the web app

---

## Environment Configuration

### Step 1: Create Environment File

Copy the example environment file:
```bash
cp .env.example .env
```

### Step 2: Edit Environment Variables

Open `.env` in a text editor:
```bash
nano .env
```

Add your credentials:
```env
# Flask Configuration
SECRET_KEY=your_random_secret_key_here
FLASK_ENV=production

# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Optional: Database Configuration
# DATABASE_URL=sqlite:///data/music_sync.db

# Optional: Server Configuration
# HOST=0.0.0.0
# PORT=5000
```

### Step 3: Generate Secret Key

Generate a secure random secret key:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Copy the output and paste it into your `.env` file.

---

## Database Initialization

The database is automatically initialized when you first run the application. However, if you need to manually initialize it:

```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

---

## Troubleshooting

### Spotify OAuth Errors

**Error**: `invalid_client` or `INVALID_CLIENT: Invalid redirect URI`

**Solution**: 
- Check that your redirect URI in `.env` matches the one in Spotify Dashboard
- Make sure there are no trailing slashes
- Verify you're using the correct protocol (http vs https)

**Error**: `unsupported_response_type`

**Solution**: 
- This usually means OAuth is not configured correctly
- Make sure you're using the Authorization Code flow
- Check that you have both Client ID and Client Secret

### YouTube Music Authentication Errors

**Error**: `Authentication failed`

**Solution**:
- Re-run the OAuth setup: `ytmusicapi oauth`
- Make sure you're logged into the correct Google account
- Try the manual header extraction method

**Error**: `Headers expired`

**Solution**:
- YouTube Music tokens expire after some time
- Re-generate your `oauth.json` file
- Upload the new file to Music Sync

### General Issues

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements-web.txt
```

**Error**: `Port already in use`

**Solution**:
```bash
# Find and kill the process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
export PORT=8080
python3 app.py
```

**Error**: `Database locked`

**Solution**:
- Close any other instances of the app
- Delete `music_sync.db` and restart (this will delete all data!)

---

## Next Steps

Once you've completed the setup:

1. ✅ Start the application: `python3 app.py`
2. ✅ Open your browser to `http://localhost:5000`
3. ✅ Register a new user account
4. ✅ Connect Spotify (click "Connect Spotify")
5. ✅ Upload YouTube Music headers
6. ✅ Start syncing playlists!

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Getting Help

If you're still having issues:
- Check the [GitHub Issues](https://github.com/yourusername/spotify_to_ytmusic/issues)
- Read the [FAQ section](README.md#faq)
- Ask in [GitHub Discussions](https://github.com/yourusername/spotify_to_ytmusic/discussions)
