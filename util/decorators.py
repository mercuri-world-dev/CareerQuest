
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or not hasattr(current_user, 'id'):
                return redirect(url_for('auth.login'))
            
            if not any(current_user.has_role(role) for role in roles):
                flash('You do not have permission to access this page.', 'warning')
                return redirect(url_for('main.index'))
                
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper