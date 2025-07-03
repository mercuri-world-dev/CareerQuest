from flask import Blueprint, render_template

from features.jobs.util.parse_response import parse_jobs_response
from services.api.jobspy import jobspy_fetch_jobs
from util.decorators import sb_login_required
from util.models import Site

preview_bp = Blueprint('preview', __name__, template_folder='templates', static_folder='static')

@sb_login_required
@preview_bp.route('/jobs')
def preview_jobs():
  resp = jobspy_fetch_jobs(
      site_name="linkedin",
      search_term="software engineer",
      location="San Francisco, CA",
      results_wanted=10,
      hours_old=72,
    )
  if not resp.is_success():
    return render_template('preview_jobs.html', error="Failed to fetch jobs: " + resp.error)
  data = resp.data
  if not isinstance(data, list):
    return render_template('preview_jobs.html', error="Invalid response format: expected a list of jobs")
  if not data:
    return render_template('preview_jobs.html', error="No jobs found")
  jobs_res = parse_jobs_response(Site.LINKEDIN, data)
  if not jobs_res.is_success():
    return render_template('preview_jobs.html', error="Failed to parse jobs: " + jobs_res.error)
  jobs = jobs_res.data
  return render_template('preview_jobs.html', jobs=jobs)