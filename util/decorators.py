from functools import wraps
from flask import flash, redirect, url_for

from util.auth import check_has_profile, fetch_user_role, get_access_token, is_authenticated

def role_required(required_roles: list):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_token = get_access_token()
            if not access_token:
                flash('You must be logged in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = fetch_user_role(access_token)
            if user_role is None or user_role not in required_roles:
                flash('You do not have permission to access this page (inadequate role).', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs) 
        return decorated_function
    return wrapper

def sb_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper

def profile_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        access_token = get_access_token()
        if not access_token:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        has_profile = check_has_profile(access_token)
        if not has_profile:
            flash('You must complete your profile to access this page.', 'warning')
            return redirect(url_for('users.profile'))
        return fn(*args, **kwargs)
    return wrapper