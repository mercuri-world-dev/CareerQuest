from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user
from db.datasource import add_role_to_user
from util.auth import fetch_user_permissions, create_jwt_token
from flask import make_response

from main.supabase_client import get_supabase

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/static/auth')

def set_jwt_cookie_and_redirect(user_id):
    permissions = fetch_user_permissions(user_id)
    jwt_token = create_jwt_token(user_id, permissions)
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('access_token', jwt_token, httponly=True, secure=True)
    flash('Login successful!', 'message')
    return resp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    print(url_for('auth.callback'))
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
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        except Exception as e:
            flash('Login failed: ' + str(e), 'error')
            return redirect(url_for('auth.login'))
        user = supabase.auth.get_user()
        if not user or not user.user:
            flash('Login failed: User not found', 'error')
            return redirect(url_for('auth.login'))
        return set_jwt_cookie_and_redirect(user.user.id)
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

@auth_bp.route('/callback')
def callback():
    supabase = get_supabase()
    user = supabase.auth.get_user()
    account_type = session.pop('pending_account_type', None)
    if user and user.user:
        if account_type:
            res = add_role_to_user(supabase, user.user.id, account_type)
            if res.error:
                flash('Failed to set account type: ' + res.error.message, 'error')
                return redirect(url_for('auth.login'))
        return set_jwt_cookie_and_redirect(user.user.id)
    flash('Login failed: User not found', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    supabase = get_supabase()
    if request.method == 'POST':
        account_type = request.form.get('account_type', 'user')
        register_method = request.form.get('register_method', 'email')
        print(register_method)

        if register_method == 'google':
            session['pending_account_type'] = account_type
            return redirect(url_for('auth.register_google'))

        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Email and password are required', 'warning')
            return redirect(url_for('auth.register'))
        try:
            res = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password
                }
            )
            add_role_to_user(supabase, res.user.id, account_type)
        except Exception as e:
            flash('Registration failed: ' + str(e), 'error')
            return redirect(url_for('auth.register'))
        user = res.user
        if not user:
            flash('Registration failed: User not found', 'error')
            return redirect(url_for('auth.register'))
        return set_jwt_cookie_and_redirect(user.id)
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
    resp = redirect(url_for('main.index'))
    resp = make_response(resp)
    resp.set_cookie('access_token', '', expires=0)
    return resp