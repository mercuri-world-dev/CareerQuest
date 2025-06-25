from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import logout_user
from util.anonymize_email import anonymize_email
from util.auth import fetch_permissions, create_jwt_token, fetch_user_roles, get_supabase_user
from flask import make_response

from main.supabase_client import get_supabase

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/static/auth')

def set_jwt_cookie_and_redirect(user_id):
    roles = fetch_user_roles(user_id)
    permissions = fetch_permissions(roles)
    jwt_token = create_jwt_token(user_id, permissions, roles)
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('access_token', jwt_token, httponly=True, secure=True)
    return resp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    supabase = get_supabase()
    if request.method == 'POST':
        user = get_supabase_user()
        if user and user.id:
            try:
                resp = logout_user()
            except Exception as e:
                flash('Logout failed: ' + str(e), 'error')
                return redirect(url_for('auth.login'))
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
        user = res.user
        if not user or not user.id:
            flash('Login failed: User not found', 'error')
            return redirect(url_for('auth.login'))
        return set_jwt_cookie_and_redirect(user.id)
    return render_template('login.html')

@auth_bp.route('/login/google')
def login_google():
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
    code = request.args.get('code')
    if not code:
        flash('No code provided in callback', 'error')
        return redirect(url_for('auth.login'))
    supabase = get_supabase()
    try:
        exchange = supabase.auth.exchange_code_for_session({ "auth_code": code })
        if not exchange or not exchange.session:
            flash('OAuth callback failed: could not exchange code for session', 'error')
            return redirect(url_for('auth.login'))
        session_resp = exchange.session
        if not session_resp or not session_resp.user:
            flash('OAuth callback failed: could not get user session', 'error')
            return redirect(url_for('auth.login'))
        user = session_resp.user
        if not user or not user.id:
            flash('OAuth callback failed: User not found', 'error')
            return redirect(url_for('auth.login'))
        supabase.table('users').upsert({
            'user_id': user.id,
            'anonymized_email': anonymize_email(user.email) if user.email else None,
        }).execute()
    except Exception as e:
        flash('OAuth callback failed: ' + str(e), 'error')
        return redirect(url_for('auth.login'))
    return set_jwt_cookie_and_redirect(user.id)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.form.get('register_method') == 'google':
        return redirect(url_for('auth.login_google'))
    supabase = get_supabase()
    if request.method == 'POST':
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
        except Exception as e:
            flash('Registration failed: ' + str(e), 'error')
            return redirect(url_for('auth.register'))
        user = res.user
        if not user:
            flash('Registration failed: User not found', 'error')
            return redirect(url_for('auth.register'))
        supabase.table('users').upsert({
            'user_id': user.id,
            'anonymized_email': anonymize_email(user.email) if user.email else None,
        }).execute()
        return set_jwt_cookie_and_redirect(user.id)
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_out()
    except Exception as e:
        flash('Logout failed: ' + str(e), 'error')
    resp = redirect(url_for('auth.login'))
    resp = make_response(resp)
    resp.set_cookie('access_token', '', expires=0)
    return resp