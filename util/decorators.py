from functools import wraps

from flask import flash, redirect, request, url_for

from util.auth import get_supabase_user, verify_jwt_token
from util.lookup import get_permission_name_to_id, get_role_name_to_id

# TODO: RBAC with Supabase hooks
def permission_required(required_permission):
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
            # Accept name or id
            if isinstance(required_permission, str):
                perm_id = get_permission_name_to_id().get(required_permission)
            else:
                perm_id = required_permission
            if perm_id not in permissions:
                flash('You do not have permission to access this page (inadequate permissions).', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

def role_required(required_role):
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
            roles = payload.get('roles', [])
            # Accept name or id
            if isinstance(required_role, str):
                role_id = get_role_name_to_id().get(required_role)
            else:
                role_id = required_role
            if role_id not in roles:
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