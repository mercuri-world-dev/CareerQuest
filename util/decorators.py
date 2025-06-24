
from functools import wraps

from flask import flash, redirect, session, url_for
from flask_login import current_user


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = session.get('supabase_user')
            if not user:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = user.get('user_metadata', {}).get('account_type')
            if user_role not in roles:
                flash('You do not have permission to access this page.', 'warning')
                return redirect(url_for('main.index'))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def sb_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session.get('supabase_user')
        if not user:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper