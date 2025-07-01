from flask import Blueprint, jsonify, render_template, request
from util.decorators import sb_login_required
from main.supabase_client import get_supabase
from features.jobs import api

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static', static_url_path='/static/jobs')

def get_rendered_job_cards(include_compatibility=False):
    jobs = api.fetch_jobs(include_compatibility)
    return [render_template('components/job_card.html', job=job, include_compatibility=include_compatibility) for job in jobs]

@jobs_bp.route('/jobs')
@sb_login_required
def all_jobs():
    rendered_jobs = get_rendered_job_cards()
    return render_template('all_jobs.html', rendered_jobs=rendered_jobs)

@jobs_bp.route('/rendered/job_cards')
@sb_login_required
def rendered_job_cards():
    include_compatibility = request.args.get('include_compatibility', 'false').lower() == 'true'
    rendered = get_rendered_job_cards(include_compatibility)
    return jsonify(rendered)

@jobs_bp.route('/jobs/<job_id>')
@sb_login_required
def job_details(job_id):
    job = api.fetch_job(job_id)
    return render_template('job_details.html', job=job)
    