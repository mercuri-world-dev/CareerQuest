from functools import wraps

from flask import flash, json, jsonify, redirect, session, url_for

from util.auth import fetch_user_role, get_supabase_user

def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            supabase_token = json.loads(session.get('supabase.auth.token'))
            if not supabase_token:
                return redirect(url_for('auth.login'))
            token = supabase_token.get('access_token')
            if not token:
                flash('You must be logged in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            user_role = fetch_user_role(token)
            if user_role is None or required_role not in user_role:
                flash('You do not have permission to access this page (inadequate role).', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

def sb_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_supabase_user()
        if not user:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper