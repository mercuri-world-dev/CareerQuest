from flask import Blueprint, flash, jsonify, redirect, render_template, session, url_for
from flask_login import current_user, logout_user

from util.auth import fetch_user_role, get_access_token, is_authenticated

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

@main_bp.route('/')
def index():
    if is_authenticated():
        if fetch_user_role(get_access_token()) in ['admin', 'content_manager', 'elevated_content_manager']:
            return redirect(url_for('cms.dashboard'))
        return redirect(url_for('users.dashboard')) 
    return render_template('index.html')

# Debug
# TODO: Remove this route in production
@main_bp.route('/debug_auth')
def debug_auth():
    debug_info = {
        "is_authenticated": current_user.is_authenticated,
        "is_active": current_user.is_active if hasattr(current_user, 'is_active') else "N/A",
        "is_anonymous": current_user.is_anonymous if hasattr(current_user, 'is_anonymous') else "N/A",
        "user_type": str(type(current_user)),
        "current_user_id": getattr(current_user, 'id', None)
    }
    return jsonify(debug_info)

@main_bp.route('/clear_session')
def clear_session():
    """Emergency route to clear session data if login/logout issues occur"""
    session.clear()
    logout_user()
    flash('Session cleared successfully', 'message')
    return redirect(url_for('main.index'))