from flask import Blueprint, redirect, render_template, url_for

from util.auth import fetch_user_role, get_access_token, is_authenticated

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

@main_bp.route('/')
def index():
    if is_authenticated():
        if fetch_user_role(get_access_token()) in ['admin', 'content_manager', 'elevated_content_manager']:
            return redirect(url_for('cms.dashboard'))
        return redirect(url_for('users.dashboard')) 
    return render_template('index.html')

@main_bp.route('/notfound')
def not_found():
    return render_template('notfound.html'), 404