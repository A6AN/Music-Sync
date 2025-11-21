"""
Database models - imported after db is initialized
"""
from datetime import datetime
import json

# Global db instance to be set by init_models
db = None
user_mixin_class = None


def init_models(database, user_mixin):
    """Initialize models with database instance"""
    global db, user_mixin_class
    db = database
    user_mixin_class = user_mixin


class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    spotify_creds = db.relationship('SpotifyCredentials', backref='user', uselist=False, cascade='all, delete-orphan')
    ytmusic_creds = db.relationship('YTMusicCredentials', backref='user', uselist=False, cascade='all, delete-orphan')
    sync_history = db.relationship('SyncHistory', backref='user', cascade='all, delete-orphan', order_by='SyncHistory.started_at.desc()')
    
    # Flask-Login integration
    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

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
            if not self.access_token or not self.token_expires_at:
                return False
            return datetime.utcnow() < self.token_expires_at

    class YTMusicCredentials(db.Model):
        """YouTube Music credentials per user"""
        __tablename__ = 'ytmusic_credentials'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
        headers_json = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def get_headers(self):
            if self.headers_json:
                return json.loads(self.headers_json)
            return None
        
        def set_headers(self, headers_dict):
            self.headers_json = json.dumps(headers_dict)

    class SyncHistory(db.Model):
        """Track sync operations"""
        __tablename__ = 'sync_history'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        sync_type = db.Column(db.String(50), nullable=False)
        direction = db.Column(db.String(20))
        playlist_name = db.Column(db.String(255))
        source_id = db.Column(db.String(255))
        destination_id = db.Column(db.String(255))
        status = db.Column(db.String(20), default='running')
        tracks_total = db.Column(db.Integer, default=0)
        tracks_synced = db.Column(db.Integer, default=0)
        tracks_failed = db.Column(db.Integer, default=0)
        error_message = db.Column(db.Text)
        started_at = db.Column(db.DateTime, default=datetime.utcnow)
        completed_at = db.Column(db.DateTime)
    
    return User, SpotifyCredentials, YTMusicCredentials, SyncHistory
