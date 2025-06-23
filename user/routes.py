from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from database import db, Job
from util.decorators import role_required

user_bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', static_url_path='/static/user')

@user_bp.route('/dashboard')
@login_required
@role_required('user')
def dashboard():
    return render_template('dashboard.html')

@user_bp.route('/job_compatibility/<job_id>')
@login_required
@role_required('user')
def job_compatibility(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        flash('Job not found')
        return redirect(url_for('all_jobs'))
        
    return render_template('job_compatibility.html', job=job)