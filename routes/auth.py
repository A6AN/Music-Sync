"""
Authentication routes: login, register, logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    from flask import current_app
    User = current_app.User
    db = current_app.db
    bcrypt = current_app.bcrypt
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long', 'danger')
            return render_template('auth/register.html')
        
        if not email or '@' not in email:
            flash('Please provide a valid email address', 'danger')
            return render_template('auth/register.html')
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    from flask import current_app
    User = current_app.User
    db = current_app.db
    bcrypt = current_app.bcrypt
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in user
            print(f"DEBUG: Attempting to log in user: {user.username}, ID: {user.id}, is_active: {user.is_active}")
            result = login_user(user, remember=remember)
            print(f"DEBUG: login_user returned: {result}")
            print(f"DEBUG: current_user.is_authenticated: {current_user.is_authenticated}")
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """User logout"""
    from flask import session
    print(f"DEBUG: Logout called for user: {current_user.username}")
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out successfully', 'success')
    print("DEBUG: User logged out, redirecting to index")
    response = redirect(url_for('index'))
    response.set_cookie('session', '', expires=0)  # Clear session cookie
    return response
