from flask import Blueprint, render_template, redirect, request, url_for, flash

from util.supabase.supabase_client import get_supabase
from util.auth import check_has_profile, refresh_access_token
from util.decorators import sb_login_required

user_bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', static_url_path='/static/user')

@user_bp.route('/dashboard')
@sb_login_required
def dashboard():
    return render_template('dashboard.html')

@user_bp.route('/profile', methods=['GET', 'POST'])
@sb_login_required
def profile():
    supabase = get_supabase()
    profile_resp = supabase.table('user_profiles').select('*').limit(1).execute() # Secure (RLS)
    profile = profile_resp.data[0] if profile_resp.data else None
    if request.method == 'POST':
        try:
            accommodations = request.form.get('accommodations', '')
            accommodations_list = [item.strip() for item in accommodations.split(',') if item.strip()]

            profile_data = {
                "age_range": request.form.get('age_range'),
                "hours_per_week": request.form.get('hours_per_week'),
                "location": request.form.get('location'),
                "accommodations": accommodations_list,
                "educational_background": request.form.get('educational_background'),
                "remote_preference": request.form.get('remote_preference') == 'on',
                "hybrid_preference": request.form.get('hybrid_preference') == 'on',
                "in_person_preference": request.form.get('in_person_preference') == 'on',
            }

            if profile and profile.get('id'):
                profile_data['id'] = profile['id']

            resp = supabase.table('user_profiles').upsert(profile_data).execute()
            flash('User profile updated successfully!', 'message')
            try:
                access_token = request.cookies.get('supabase.auth.token')
                if not check_has_profile(access_token):
                    refresh_access_token()
            except Exception as e:
                print(f"Error refreshing access token: {e}")
                flash('There was an error refreshing your session. Please log in again.', 'error')
                return redirect(url_for('users.dashboard'))
            return render_template('profile.html', profile=resp.data[0] if resp.data else None)
        except Exception as e:
            print(f"Error updating user profile: {e}")
            flash('There was an error updating the user profile. Please try again.', 'error')
            return render_template('profile.html', profile=profile if profile else None)
    return render_template('profile.html', profile=profile if profile else None)