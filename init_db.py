#!/usr/bin/env python3
"""Initialize the database"""

from app import app, db

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
    print("Tables created:")
    print("- users")
    print("- spotify_credentials")
    print("- ytmusic_credentials")
    print("- sync_history")
