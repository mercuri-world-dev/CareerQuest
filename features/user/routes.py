from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required

from database import db, Job
from util.decorators import role_required, sb_login_required

user_bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', static_url_path='/static/user')

@user_bp.route('/dashboard')
@sb_login_required
@role_required('user')
def dashboard():
    return render_template('dashboard.html')

@user_bp.route('/job_recommendations')
@sb_login_required
@role_required('user')
def job_recommendations():
    return render_template('job_recommendations.html')

@user_bp.route('/job_compatibility/<job_id>')
@sb_login_required
@role_required('user')
def job_compatibility(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.all_jobs'))
        
    return render_template('job_compatibility.html', job=job)

@user_bp.route('/profile', methods=['GET', 'POST'])
@sb_login_required
@role_required('user')
def profile():
    if request.method == 'POST':
        current_user.age_range = request.form.get('age_range')
        hours = request.form.get('hours_per_week')
        current_user.hours_per_week = int(hours) if hours else None
        current_user.location = request.form.get('location')
        current_user.educational_background = request.form.get('educational_background')
        current_user.remote_preference = request.form.get('remote_preference') == 'on'
        current_user.hybrid_preference = request.form.get('hybrid_preference') == 'on'
        current_user.in_person_preference = request.form.get('in_person_preference') == 'on'
        
        # Handle accommodations as a list
        accommodations = request.form.get('accommodations', '')
        accommodations_list = [item.strip() for item in accommodations.split(',') if item.strip()]
        current_user.set_accommodations_list(accommodations_list)
        
        db.session.commit()
        flash('Profile updated successfully!', 'message')
        return redirect(url_for('users.profile'))
        
    return render_template('profile.html')