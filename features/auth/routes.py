from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user

from main.supabase_client import get_supabase

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/static/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    supabase = get_supabase()
    if request.method == 'POST':
        if current_user.is_authenticated and hasattr(current_user, 'id'):
            logout_user()
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Email and password are required', 'warning')
            return redirect(url_for('auth.login'))
        
        try:
            res = supabase.auth.sign_in_with_password(
                {
                    "email": email, 
                    "password": password
                }
            )
        except Exception as e:
            flash('Login failed: ' + str(e), 'error')
            return redirect(url_for('auth.login'))
        user = supabase.auth.get_user()
        if not user or not user.user:
            flash('Login failed: User not found', 'error')
            return redirect(url_for('auth.login'))
        session['supabase_user'] = user.user
        return redirect(url_for('main.index'))
    return render_template('login.html')

@auth_bp.route('/login/google')
def google_login():
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_oauth(
            {
                'provider': 'google',
                'options': {
                    'redirect_to': url_for('auth.callback', _external=True)
                }
            }
        )
    except Exception as e:
        flash('Google login failed: ' + str(e), 'error')
        return redirect(url_for('auth.login'))
    return redirect(res.url)

@auth_bp.route('/login/callback')
def callback():
    supabase = get_supabase()
    user = supabase.auth.get_user()
    account_type = session.pop('pending_account_type', None)
    if user and user.user and account_type:
        supabase.auth.update_user(
            {
                "data": {
                    "account_type": account_type
                }
            }
        )
    flash('Login successful!', 'message')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    supabase = get_supabase()
    if request.method == 'POST':
        account_type = request.form.get('account_type', 'user')
        register_method = request.form.get('register_method', 'email')

        if register_method == 'google':
            session['pending_account_type'] = account_type
            return redirect(url_for('auth.register_google'))

        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        if not email or not password or not username:
            flash('Email, password, and username are required', 'warning')
            return redirect(url_for('auth.register'))
        try: 
            res = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "username": username,
                            "account_type": account_type
                        }
                    }
                }
            )
        except Exception as e:
            flash('Registration failed: ' + str(e), 'error')
            return redirect(url_for('auth.register'))
        flash('Registration successful!', 'message')
        return redirect(url_for('main.index'))
    return render_template('register.html')

@auth_bp.route('/register/google')
def register_google():
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_oauth(
            {
                'provider': 'google',
                'options': {
                    'redirect_to': url_for('auth.callback', _external=True)
                }
            }
        )
    except Exception as e:
        flash('Google registration failed: ' + str(e), 'error')
        return redirect(url_for('auth.register'))
    return redirect(res.url)

@auth_bp.route('/logout')
def logout():
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_out()
    except Exception as e:
        flash('Logout failed: ' + str(e), 'error')
    return redirect(url_for('main.index'))