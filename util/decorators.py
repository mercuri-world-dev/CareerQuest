
from functools import wraps

from flask import flash, redirect, request, session, url_for
from flask_login import current_user

from util.auth import get_supabase_user, verify_jwt_token

def role_required(required_permission):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get('access_token')
            if not token:
                flash('You must be logged in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            payload = verify_jwt_token(token)
            if not payload:
                flash('Invalid or expired session. Please log in again.', 'error')
                return redirect(url_for('auth.login'))
            permissions = payload.get('permissions', [])
            if required_permission not in permissions:
                flash('You do not have permission to access this page.', 'error')
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