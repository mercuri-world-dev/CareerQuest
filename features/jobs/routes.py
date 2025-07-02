from flask import Blueprint, jsonify, render_template, request
from util.auth import check_has_profile, get_access_token
from util.decorators import profile_required, sb_login_required
from features.jobs import api

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static', static_url_path='/static/jobs')

def get_rendered_job_cards(include_compatibility=False, include_factors=False):
    if include_compatibility and include_factors:
        jobs_res = api.fetch_jobs_with_compatibility_factors()
    elif include_compatibility:
        jobs_res = api.fetch_jobs_with_compatibility()
    else:
        jobs_res = api.fetch_jobs()
    if not jobs_res.is_success():
        return [render_template('components/job_error.html', msg=jobs_res.error)]
    jobs = jobs_res.data
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
    job_res = api.fetch_job_with_compatibility_factors(job_id)
    if not job_res.is_success():
        return render_template('job_details.html', err=job_res.error)
    job = job_res.data
    return render_template('job_details.html', job=job)

@jobs_bp.route('/recommended_jobs')
@sb_login_required
@profile_required
def recommended_jobs():
    jobs_res = api.fetch_jobs_with_compatibility()
    if not jobs_res.is_success():
        return render_template('recommended_jobs.html', err=jobs_res.error)
    jobs = jobs_res.data
    successful_jobs = [job_res.data for job_res in jobs if job_res.is_success()]
    sorted_jobs = sorted(successful_jobs, key=lambda j: j.compatibility_score, reverse=True)[:10]
    rendered_jobs = [
        render_template('components/job_card.html', job=job, include_compatibility=True)
        for job in sorted_jobs
    ]
    access_token = get_access_token()
    return render_template(
        'recommended_jobs.html',
        rendered_jobs=rendered_jobs,
        include_compatibility=True,
        has_profile=check_has_profile(access_token) if access_token else False
    )