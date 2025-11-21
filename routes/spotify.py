"""
Spotify authentication and management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import os
import json
from datetime import datetime, timedelta

bp = Blueprint('spotify', __name__, url_prefix='/spotify')


@bp.route('/auth')
@login_required
def auth():
    """Initiate Spotify OAuth flow"""
    # This will be similar to spotify_backup.py authorization
    return render_template('spotify/auth.html')


@bp.route('/callback')
@login_required
def callback():
    """Handle Spotify OAuth callback"""
    # Get authorization code from query parameters
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'Spotify authorization failed: {error}', 'danger')
        return redirect(url_for('spotify.auth'))
    
    if not code:
        flash('No authorization code received', 'danger')
        return redirect(url_for('spotify.auth'))
    
    # Exchange code for access token
    from flask import current_app
    import requests
    
    client_id = current_app.config['SPOTIFY_CLIENT_ID']
    client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']
    redirect_uri = request.host_url.rstrip('/') + url_for('spotify.callback')
    
    # Exchange authorization code for access token
    token_url = 'https://accounts.spotify.com/api/token'
    
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    })
    
    if response.status_code != 200:
        flash(f'Failed to get access token: {response.text}', 'danger')
        return redirect(url_for('spotify.auth'))
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data.get('expires_in', 3600)
    
    # Save credentials
    db = current_app.db
    SpotifyCredentials = current_app.SpotifyCredentials
    
    creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    if not creds:
        creds = SpotifyCredentials(user_id=current_user.id)
        db.session.add(creds)
    
    creds.access_token = access_token
    creds.refresh_token = refresh_token
    creds.token_expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
    creds.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Spotify connected successfully!', 'success')
    return redirect(url_for('dashboard'))


@bp.route('/save-token', methods=['POST'])
@login_required
def save_token():
    """Save Spotify access token from OAuth"""
    from flask import current_app
    db = current_app.db
    SpotifyCredentials = current_app.SpotifyCredentials
    
    data = request.get_json()
    print(f"DEBUG: save_token received data: {data}")
    access_token = data.get('access_token')
    expires_in = data.get('expires_in', 3600)
    
    print(f"DEBUG: access_token length: {len(access_token) if access_token else 0}, expires_in: {expires_in}")
    
    if not access_token:
        return {'success': False, 'error': 'No access token provided'}, 400
    
    # Get or create Spotify credentials
    creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    if not creds:
        print(f"DEBUG: Creating new Spotify credentials for user {current_user.id}")
        creds = SpotifyCredentials(user_id=current_user.id)
        db.session.add(creds)
    else:
        print(f"DEBUG: Updating existing Spotify credentials for user {current_user.id}")
    
    creds.access_token = access_token
    creds.token_expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
    creds.updated_at = datetime.utcnow()
    
    db.session.commit()
    print(f"DEBUG: Spotify credentials saved successfully")
    
    flash('Spotify connected successfully!', 'success')
    return {'success': True}


@bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Spotify account"""
    from flask import current_app
    db = current_app.db
    SpotifyCredentials = current_app.SpotifyCredentials
    
    creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    if creds:
        db.session.delete(creds)
        db.session.commit()
        flash('Spotify disconnected', 'info')
    
    return redirect(url_for('dashboard'))


@bp.route('/playlists')
@login_required
def playlists():
    """List user's Spotify playlists"""
    from flask import current_app
    import requests
    SpotifyCredentials = current_app.SpotifyCredentials
    
    creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    
    if not creds or not creds.is_valid():
        flash('Please connect your Spotify account first', 'warning')
        return redirect(url_for('spotify.auth'))
    
    # Fetch playlists from Spotify API
    try:
        headers = {
            'Authorization': f'Bearer {creds.access_token}'
        }
        response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
        
        if response.status_code == 200:
            playlists_data = response.json().get('items', [])
        else:
            flash(f'Failed to fetch playlists: {response.status_code}', 'danger')
            playlists_data = []
    except Exception as e:
        flash(f'Error fetching playlists: {str(e)}', 'danger')
        playlists_data = []
    
    return render_template('spotify/playlists.html', playlists=playlists_data)


@bp.route('/playlists-data')
@login_required
def playlists_data():
    """Return playlists as JSON for AJAX requests"""
    from flask import current_app
    import requests
    SpotifyCredentials = current_app.SpotifyCredentials
    
    creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    
    if not creds or not creds.is_valid():
        return jsonify([])
    
    try:
        headers = {
            'Authorization': f'Bearer {creds.access_token}'
        }
        response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
        
        if response.status_code == 200:
            return jsonify(response.json().get('items', []))
        else:
            return jsonify([])
    except Exception as e:
        return jsonify([])


@bp.route('/backup', methods=['POST'])
@login_required
def backup():
    """Trigger Spotify backup to download playlists"""
    from spotify2ytmusic.spotify_backup import SpotifyAPI
    from flask import current_app
    SpotifyCredentials = current_app.SpotifyCredentials
    
    creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    
    if not creds or not creds.is_valid():
        return {'success': False, 'error': 'Spotify not connected'}, 400
    
    try:
        # Initialize Spotify API
        sp = SpotifyAPI(creds.access_token)
        
        # Create user data directory
        user_data_dir = os.path.join('user_data', str(current_user.id))
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Fetch playlists and liked songs
        playlists = sp.list('me/playlists')
        liked_songs = sp.list('me/tracks')
        
        # Save to file
        playlists_file = os.path.join(user_data_dir, 'playlists.json')
        data = {
            'playlists': playlists,
            'liked': liked_songs
        }
        
        with open(playlists_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        flash('Spotify playlists backed up successfully!', 'success')
        return {'success': True, 'playlists_count': len(playlists)}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
