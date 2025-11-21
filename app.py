#!/usr/bin/env python3
"""
Spotify ↔ YouTube Music Web Application
Multi-user platform for syncing music between streaming services
"""

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import json
import os
import secrets

# Initialize Flask app
app = Flask(__name__)

# Load SECRET_KEY from .env file
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
print(f"DEBUG: Using SECRET_KEY (first 16 chars): {app.config['SECRET_KEY'][:16]}...")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///music_sync.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'user_data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SPOTIFY_CLIENT_ID'] = os.environ.get('SPOTIFY_CLIENT_ID', '329e873b7a9f45a4a8128770e084e27c')
app.config['SPOTIFY_CLIENT_SECRET'] = os.environ.get('SPOTIFY_CLIENT_SECRET', '')

# Session configuration for Flask-Login
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Database Models
class User(UserMixin, db.Model):
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


# Make models available to blueprints via app
app.User = User
app.SpotifyCredentials = SpotifyCredentials  
app.YTMusicCredentials = YTMusicCredentials
app.SyncHistory = SyncHistory
app.db = db
app.bcrypt = bcrypt


# Import and register blueprints
from routes import auth, spotify, ytmusic, sync
app.register_blueprint(auth.bp)
app.register_blueprint(spotify.bp)
app.register_blueprint(ytmusic.bp)
app.register_blueprint(sync.bp)


@app.route('/')
def index():
    """Home page / landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing sync status and options"""
    return render_template('dashboard.html', user=current_user)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    print(f"DEBUG: load_user called with user_id: {user_id}, type: {type(user_id)}")
    try:
        user = User.query.get(int(user_id))
        print(f"DEBUG: load_user found user: {user}, type: {type(user)}, class: {user.__class__ if user else None}")
        if user:
            print(f"DEBUG: user.is_active: {user.is_active}, user.is_authenticated: {user.is_authenticated}")
        return user
    except Exception as e:
        print(f"DEBUG: load_user ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    app.run(host=host, port=port, debug=debug_mode)
