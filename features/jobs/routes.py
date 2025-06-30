from flask import Blueprint, jsonify, render_template, request
from util.decorators import sb_login_required
from main.supabase_client import get_supabase
from features.jobs import api

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static', static_url_path='/static/jobs')

# MOCK_JOB = {
#     "id": "1",
#     "company_profile_id": "123",
#     "company_name": "Tech Innovations Inc.",
#     "role_name": "Software Engineer",
#     "industry": ["Technology"],
#     "weekly_hours": "40",
#     "work_mode": "Remote",
#     "location": "San Francisco, CA",
#     "qualifications": ["Bachelor's degree in Computer Science or related field"],
#     "accommodations": ["Wheelchair accessible office", "flexible work hours"],
#     "application_period_start": "2023-10-01",
#     "application_period_end": "2023-11-01",
#     "application_status": "Open",
#     "job_type": "Full-time",
#     "application_materials": ["Resume", "Cover Letter"],
#     "job_description": "We are looking for a skilled software engineer to join our team. The ideal candidate will have experience in full-stack development and a passion for building innovative solutions.",
#     "application_link": "https://techinnovations.com/careers/apply",
#     "created_at": "2023-09-01T12:00:00Z",
#     "updated_at": "2023-09-15T12:00:00Z"
# }

def get_rendered_job_cards():
    jobs = api.get_jobs()
    # jobs = [MOCK_JOB]  # For testing purposes, using a mock job
    return [render_template('components/job_card.html', job=job) for job in jobs]

@jobs_bp.route('/all_jobs')
@sb_login_required
def all_jobs():
    rendered_jobs = get_rendered_job_cards()
    return render_template('all_jobs.html', rendered_jobs=rendered_jobs)

@jobs_bp.route('/rendered/job_cards')
@sb_login_required
def rendered_job_cards():
    rendered = get_rendered_job_cards()
    return jsonify(rendered)