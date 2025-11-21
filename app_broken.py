#!/usr/bin/env python3
"""
Spotify ↔ YouTube Music Web Application
Multi-user platform for syncing music between streaming services
"""

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import secrets

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///music_sync.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'user_data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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

# Initialize models
from flask_login import UserMixin
import db_models
User, SpotifyCredentials, YTMusicCredentials, SyncHistory = db_models.init_models(db, UserMixin)

# Make models available to other modules
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
