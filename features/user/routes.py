from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, request, url_for, flash

from main.supabase_client import get_supabase
from util.auth import get_current_user_id
from util.decorators import sb_login_required

user_bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', static_url_path='/static/user')

@user_bp.route('/dashboard')
@sb_login_required
def dashboard():
    return render_template('dashboard.html')

# @user_bp.route('/job_recommendations')
# @sb_login_required
# def job_recommendations():
#     return render_template('job_recommendations.html')

# @user_bp.route('/job_compatibility/<job_id>')
# @sb_login_required
# def job_compatibility(job_id):
#     supabase = get_supabase()
#     job = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
#     if not job:
#         flash('Job not found', 'error')
#         return redirect(url_for('jobs.all_jobs'))
    
#     return render_template('job_compatibility.html', job=job)

#TODO: fix this with final user profile model  
@user_bp.route('/profile', methods=['GET', 'POST'])
@sb_login_required
def profile():
    supabase = get_supabase()
    profile_resp = supabase.table('user_profiles').select('*').eq('user_id', get_current_user_id(supabase)).limit(1).execute()
    profile = profile_resp.data
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
                "updated_at": datetime.now(tz=timezone.utc).isoformat()
            }

            resp = supabase.table('user_profiles').insert(profile_data).execute()
            flash('User profile updated successfully!', 'message')
            return render_template('profile.html', profile=resp.data[0] if resp.data else None)
        except Exception as e:
            print(f"Error updating user profile: {e}")
            flash('There was an error updating the user profile. Please try again.', 'error')
            return render_template('profile.html', profile=profile if profile else None)
        
    return render_template('profile.html', profile=profile if profile else None)