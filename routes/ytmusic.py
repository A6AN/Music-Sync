"""
YouTube Music authentication and management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import json
import re

bp = Blueprint('ytmusic', __name__, url_prefix='/ytmusic')


@bp.route('/auth')
@login_required
def auth():
    """YouTube Music authentication setup"""
    return render_template('ytmusic/auth.html')


@bp.route('/upload-headers', methods=['POST'])
@login_required
def upload_headers():
    """Upload YouTube Music headers from raw text"""
    from flask import current_app
    db = current_app.db
    YTMusicCredentials = current_app.YTMusicCredentials
    
    raw_headers = request.form.get('raw_headers', '')
    
    if not raw_headers:
        flash('No headers provided', 'danger')
        return redirect(url_for('ytmusic.auth'))
    
    try:
        # Parse raw headers into dict (similar to ytmusic_credentials.py)
        headers_dict = parse_raw_headers(raw_headers)
        
        if not headers_dict:
            flash('Could not parse headers. Please check the format.', 'danger')
            return redirect(url_for('ytmusic.auth'))
        
        # Get or create YTMusic credentials
        creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
        if not creds:
            creds = YTMusicCredentials(user_id=current_user.id)
            db.session.add(creds)
        
        creds.set_headers(headers_dict)
        creds.updated_at = db.func.now()
        
        db.session.commit()
        
        flash('YouTube Music connected successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f'Error processing headers: {str(e)}', 'danger')
        return redirect(url_for('ytmusic.auth'))


@bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect YouTube Music account"""
    from flask import current_app
    db = current_app.db
    YTMusicCredentials = current_app.YTMusicCredentials
    
    creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
    if creds:
        db.session.delete(creds)
        db.session.commit()
        flash('YouTube Music disconnected', 'info')
    
    return redirect(url_for('dashboard'))


def parse_raw_headers(raw_text):
    """
    Parse raw HTTP headers text into a dictionary
    Similar to ytmusic_credentials.py logic
    """
    headers = {}
    
    for line in raw_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith(':'):
            continue
        
        # Split on first colon
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Only include relevant headers for ytmusicapi
            if key.lower() in ['cookie', 'x-goog-authuser', 'authorization', 
                               'x-origin', 'user-agent', 'accept-language']:
                headers[key] = value
    
    # Validate that we have at least cookie
    if 'cookie' not in headers and 'Cookie' not in headers:
        return None
    
    return headers


@bp.route('/playlists')
@login_required
def playlists():
    """Display YouTube Music playlists page"""
    return render_template('ytmusic/playlists.html')


@bp.route('/api/playlists')
@login_required
def playlists_data():
    """Get YouTube Music playlists as JSON"""
    from flask import current_app, jsonify
    from ytmusicapi import YTMusic
    
    YTMusicCredentials = current_app.YTMusicCredentials
    
    creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
    if not creds:
        return jsonify({'error': 'YouTube Music not connected'}), 401
    
    try:
        ytmusic = YTMusic(auth=creds.get_headers())
        playlists = ytmusic.get_library_playlists(limit=100)
        
        # Format for frontend
        formatted = []
        for pl in playlists:
            formatted.append({
                'id': pl.get('playlistId', ''),
                'name': pl.get('title', 'Untitled'),
                'track_count': pl.get('count', 0),
                'description': pl.get('description', '')
            })
        
        return jsonify({'playlists': formatted})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
