"""
Apple Music authentication and management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import requests
import json
from datetime import datetime

bp = Blueprint('applemusic', __name__, url_prefix='/applemusic')

class AppleMusicClient:
    def __init__(self, music_user_token, developer_token):
        self.music_user_token = music_user_token
        self.developer_token = developer_token
        
    def get_headers(self):
        # Identify if developer token already has 'Bearer ' prefix
        auth_header = self.developer_token
        if not auth_header.lower().startswith('bearer '):
            auth_header = f'Bearer {auth_header}'
            
        headers = {
            'Authorization': auth_header,
            'Music-User-Token': self.music_user_token,
            'Origin': 'https://music.apple.com'
        }
        return headers

    def search(self, query, types='songs', limit=5):
        try:
            # We need to find the storefront first, usually 'us' is a safe default for search
            # but user specific search is better
            url = f'https://api.music.apple.com/v1/catalog/us/search'
            
            # Helper to get storefront if needed
            # For now default to 'us' catalog search
            
            params = {'term': query, 'types': types, 'limit': limit}
            response = requests.get(url, headers=self.get_headers(), params=params)
            
            if response.status_code == 401:
                raise Exception("Unauthorized: Tokens might be expired")
                
            return response.json()
        except Exception as e:
            print(f"Apple Music Search Error: {e}")
            return {}

    def create_playlist(self, name, description=""):
        url = 'https://api.music.apple.com/v1/me/library/playlists'
        payload = {
            "attributes": {
                "name": name,
                "description": description
            }
        }
        response = requests.post(url, headers=self.get_headers(), json=payload)
        
        if response.status_code == 401:
            raise Exception("Unauthorized: Tokens might be expired")
            
        return response.json()

    def add_tracks_to_playlist(self, playlist_id, track_ids):
        # track_ids should be list of dicts: [{'id': '123', 'type': 'songs'}]
        data = [{'id': tid, 'type': 'songs'} for tid in track_ids]
        
        url = f'https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks'
        response = requests.post(url, headers=self.get_headers(), json={'data': data})
        return response.status_code

    def get_user_playlists(self):
        url = 'https://api.music.apple.com/v1/me/library/playlists'
        try:
            response = requests.get(url, headers=self.get_headers(), params={'limit': 100})
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error fetching playlists: {e}")
        return []

    def get_playlist_tracks(self, playlist_id):
        url = f'https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks'
        try:
            response = requests.get(url, headers=self.get_headers(), params={'limit': 100})
            
            tracks = []
            if response.status_code == 200:
                data = response.json()
                tracks.extend(data.get('data', []))
                
                # Handle pagination
                next_url = data.get('next')
                while next_url:
                    if not next_url.startswith('http'):
                        next_url = 'https://api.music.apple.com' + next_url
                        
                    resp = requests.get(next_url, headers=self.get_headers())
                    if resp.status_code == 200:
                        d = resp.json()
                        tracks.extend(d.get('data', []))
                        next_url = d.get('next')
                    else:
                        break
            return tracks
        except Exception as e:
            print(f"Error fetching tracks: {e}")
            return []

@bp.route('/auth')
@login_required
def auth():
    """Render Apple Music Manual Auth Page"""
    from flask import current_app
    AppleMusicCredentials = current_app.AppleMusicCredentials
    
    creds = AppleMusicCredentials.query.filter_by(user_id=current_user.id).first()
    
    return render_template('applemusic/auth.html', creds=creds)

@bp.route('/settings', methods=['POST'])
@login_required
def save_settings():
    """Save Manual Tokens"""
    from flask import current_app
    db = current_app.db
    AppleMusicCredentials = current_app.AppleMusicCredentials
    
    token_input = request.form.get('tokens_json')
    # Or separate fields
    music_user_token = request.form.get('music_user_token')
    developer_token = request.form.get('developer_token')
    
    if not music_user_token or not developer_token:
        flash('Both tokens are required', 'danger')
        return redirect(url_for('applemusic.auth'))
        
    creds = AppleMusicCredentials.query.filter_by(user_id=current_user.id).first()
    if not creds:
        creds = AppleMusicCredentials(user_id=current_user.id)
        db.session.add(creds)
        
    creds.music_user_token = music_user_token
    creds.developer_token = developer_token
    creds.updated_at = datetime.utcnow()
    
    try:
        # Test connection
        client = AppleMusicClient(music_user_token, developer_token)
        playlists = client.get_user_playlists()
        # If no error (even if empty list), tokens are likely valid
        
        db.session.commit()
        flash('Apple Music connected successfully!', 'success')
    except Exception as e:
        flash(f'Error validating tokens: {str(e)}', 'danger')
        
    return redirect(url_for('applemusic.auth'))

@bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Apple Music"""
    from flask import current_app
    db = current_app.db
    AppleMusicCredentials = current_app.AppleMusicCredentials
    
    creds = AppleMusicCredentials.query.filter_by(user_id=current_user.id).first()
    if creds:
        db.session.delete(creds)
        db.session.commit()
        flash('Apple Music disconnected', 'info')
    
    return redirect(url_for('dashboard'))


@bp.route('/playlists-data')
@login_required
def playlists_data():
    """Return Apple Music playlists as JSON"""
    from flask import current_app
    AppleMusicCredentials = current_app.AppleMusicCredentials
    
    creds = AppleMusicCredentials.query.filter_by(user_id=current_user.id).first()
    if not creds:
        return jsonify([])
        
    try:
        client = AppleMusicClient(creds.music_user_token, creds.developer_token)
        playlists = client.get_user_playlists()
        return jsonify(playlists)
    except Exception as e:
        print(f"Error fetching AM playlists: {e}")
        return jsonify([])


