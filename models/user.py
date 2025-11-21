"""
Database models for the Music Sync application
"""

from app import db
from flask_login import UserMixin
from datetime import datetime
import json


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    spotify_creds = db.relationship('SpotifyCredentials', backref='user', uselist=False, cascade='all, delete-orphan')
    ytmusic_creds = db.relationship('YTMusicCredentials', backref='user', uselist=False, cascade='all, delete-orphan')
    sync_history = db.relationship('SyncHistory', backref='user', cascade='all, delete-orphan', order_by='SyncHistory.started_at.desc()')
    
    def __repr__(self):
        return f'<User {self.username}>'


class SpotifyCredentials(db.Model):
    """Spotify OAuth credentials per user"""
    __tablename__ = 'spotify_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    spotify_user_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_valid(self):
        """Check if token is still valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at


class YTMusicCredentials(db.Model):
    """YouTube Music credentials per user"""
    __tablename__ = 'ytmusic_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    headers_json = db.Column(db.Text)  # Stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_headers(self):
        """Parse and return headers as dict"""
        if self.headers_json:
            return json.loads(self.headers_json)
        return None
    
    def set_headers(self, headers_dict):
        """Store headers as JSON"""
        self.headers_json = json.dumps(headers_dict)


class SyncHistory(db.Model):
    """Track sync operations"""
    __tablename__ = 'sync_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sync_type = db.Column(db.String(50), nullable=False)  # 'spotify_to_ytmusic', 'ytmusic_to_spotify', 'liked_songs', etc.
    direction = db.Column(db.String(20))  # 'to_ytmusic', 'to_spotify'
    playlist_name = db.Column(db.String(255))
    source_id = db.Column(db.String(255))
    destination_id = db.Column(db.String(255))
    status = db.Column(db.String(20), default='running')  # 'running', 'completed', 'failed'
    tracks_total = db.Column(db.Integer, default=0)
    tracks_synced = db.Column(db.Integer, default=0)
    tracks_failed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<SyncHistory {self.sync_type} - {self.status}>'


class PlaylistMapping(db.Model):
    """Map playlists between services"""
    __tablename__ = 'playlist_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spotify_playlist_id = db.Column(db.String(255))
    spotify_playlist_name = db.Column(db.String(255))
    ytmusic_playlist_id = db.Column(db.String(255))
    ytmusic_playlist_name = db.Column(db.String(255))
    auto_sync = db.Column(db.Boolean, default=False)
    last_synced = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PlaylistMapping {self.spotify_playlist_name} ↔ {self.ytmusic_playlist_name}>'
