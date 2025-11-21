# Contributing to Music Sync

First off, thank you for considering contributing to Music Sync! 🎉

This project aims to make music platform synchronization easy and accessible for everyone. Whether you're fixing bugs, adding features, or improving documentation, your contributions are welcome!

## 🎯 Project Vision

Our goal is to create a **universal music sync platform** that supports all major streaming services. Currently, we support Spotify and YouTube Music, but we're eager to expand to:

- **Apple Music** (waiting for better API access)
- **Amazon Music** (waiting for API improvements)
- **Tidal** (coming to India soon!)
- **Deezer**
- **SoundCloud**
- And more!

## 🚀 Ways to Contribute

### 1. Add New Music Platform Support

This is our **highest priority**! If you have experience with any music platform's API, please help add support:

**Priority Platforms:**
- 🍎 Apple Music API integration
- 📦 Amazon Music API integration
- 🌊 Tidal API integration
- 🎵 Deezer API integration
- ☁️ SoundCloud API integration

**What you need to do:**
1. Create a new route file: `routes/platformname.py`
2. Implement authentication (OAuth or API key)
3. Implement playlist fetching
4. Implement playlist creation
5. Add sync logic to `routes/sync.py`
6. Update UI templates to include the new platform
7. Update documentation

### 2. Fix Bugs

Found a bug? Please:
1. Check if it's already reported in [Issues](https://github.com/yourusername/spotify_to_ytmusic/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
3. Even better: Submit a PR with a fix!

### 3. Improve Features

Ideas for improvements:
- Better song matching algorithms (fuzzy matching)
- Playlist scheduling (auto-sync)
- Batch operations
- Performance optimizations
- Mobile responsiveness improvements
- Accessibility improvements
- Internationalization (i18n)

### 4. Documentation

- Fix typos or unclear instructions
- Add screenshots or GIFs
- Create video tutorials
- Translate documentation to other languages
- Add API documentation

### 5. Testing

- Write unit tests
- Write integration tests
- Test on different platforms (Windows, macOS, Linux)
- Test with different music platforms
- Report edge cases

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+
- Git
- Docker (optional, for testing deployment)
- Spotify Developer Account (for testing)

### Local Setup

1. **Fork and clone**
```bash
git clone https://github.com/YOUR_USERNAME/spotify_to_ytmusic.git
cd spotify_to_ytmusic
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements-web.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your test credentials
```

5. **Run the app**
```bash
python3 app.py
```

6. **Make your changes**

7. **Test your changes**
```bash
# Run tests (when available)
python -m pytest

# Test manually in browser
# Open http://localhost:5000
```

## 📝 Code Style Guidelines

### Python
- Follow [PEP 8](https://pep8.org/)
- Use descriptive variable names
- Add docstrings to functions
- Keep functions small and focused
- Use type hints where appropriate

Example:
```python
def sync_playlist(playlist_id: str, platform: str) -> dict:
    """
    Sync a playlist from one platform to another.
    
    Args:
        playlist_id: The ID of the playlist to sync
        platform: Target platform ('spotify' or 'ytmusic')
        
    Returns:
        dict: Sync result with status and track count
    """
    # Implementation
    pass
```

### HTML/CSS/JavaScript
- Use Bootstrap 5 classes where possible
- Keep JavaScript simple and readable
- Add comments for complex logic
- Maintain the "On Fire" color palette for consistency

### Git Commits
- Use clear, descriptive commit messages
- Follow conventional commits format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `style:` for formatting changes
  - `refactor:` for code restructuring
  - `test:` for adding tests
  - `chore:` for maintenance tasks

Examples:
```
feat: add Apple Music authentication
fix: resolve sync progress not updating
docs: add Apple Music setup guide
```

## 🔍 Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Test thoroughly** - make sure nothing breaks
3. **Follow code style** - keep it consistent
4. **Write clear PR description**:
   - What does this PR do?
   - Why is this change needed?
   - How did you test it?
   - Screenshots (if UI changes)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Tested with Docker
- [ ] Tested on production-like environment

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

## 🎵 Adding a New Music Platform

Here's a step-by-step guide to add a new platform (example: Apple Music):

### 1. Create Authentication Route

Create `routes/applemusic.py`:

```python
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
# Import platform-specific library
import applemusicpy

applemusic_bp = Blueprint('applemusic', __name__, url_prefix='/applemusic')

@applemusic_bp.route('/connect')
@login_required
def connect():
    """Initiate Apple Music OAuth flow"""
    # Implementation
    pass

@applemusic_bp.route('/callback')
@login_required
def callback():
    """Handle OAuth callback"""
    # Implementation
    pass
```

### 2. Add Database Model

Add to `app.py`:

```python
class AppleMusicCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500))
    token_expiry = db.Column(db.DateTime)
    # Add other required fields
```

### 3. Add Sync Logic

Update `routes/sync.py` to handle Apple Music syncs.

### 4. Update Templates

Add Apple Music connection button to `templates/dashboard.html`.

### 5. Update Documentation

Add setup instructions for Apple Music API credentials.

### 6. Test Everything

- Authentication flow
- Playlist fetching
- Playlist creation
- Sync in both directions

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Be patient with new contributors
- Celebrate successes together!

## 📞 Getting Help

- **Questions?** Open a [Discussion](https://github.com/yourusername/spotify_to_ytmusic/discussions)
- **Bugs?** Create an [Issue](https://github.com/yourusername/spotify_to_ytmusic/issues)
- **Need guidance?** Comment on an existing issue or PR

## 🏆 Contributors

Thank you to all our contributors! Your work makes this project possible.

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- This section will be automatically updated -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

---

**Happy Contributing! Let's build something amazing together! 🎵🔥**
