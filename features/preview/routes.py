
from flask import Blueprint, render_template, request

from features.jobs.util.parse_response import parse_jobs_response
from services.api.jobspy import jobspy_fetch_jobs
from util.decorators import sb_login_required
from util.models import Site

preview_bp = Blueprint('preview', __name__, template_folder='templates', static_folder='static')

@sb_login_required
@preview_bp.route('/jobs', methods=['GET'])
def preview_jobs():
  site_name = request.args.get('site_name', 'linkedin')
  search_term = request.args.get('search_term', 'software engineer')
  location = request.args.get('location', 'San Francisco, CA')
  results_wanted = request.args.get('results_wanted', 10, type=int)
  hours_old = request.args.get('hours_old', 72, type=int)
  is_remote = request.args.get('is_remote')
  job_type = request.args.get('job_type')

  if is_remote == 'true':
    is_remote_val = True
  elif is_remote == 'false':
    is_remote_val = False
  else:
    is_remote_val = None

  job_type_val = job_type if job_type else None

  resp = jobspy_fetch_jobs(
      site_name=str(site_name),
      search_term=str(search_term),
      location=str(location),
      results_wanted=int(results_wanted) if results_wanted is not None else 10,
      hours_old=int(hours_old) if hours_old is not None else 72,
      is_remote=is_remote_val if is_remote_val is not None else False,
      job_type=str(job_type_val) if job_type_val else None
  )
  if not resp.is_success():
    return render_template('preview_jobs.html', error="Failed to fetch jobs: " + resp.error, request=request)
  data = resp.data
  if not isinstance(data, list):
    return render_template('preview_jobs.html', error="Invalid response format: expected a list of jobs", request=request)
  if not data:
    return render_template('preview_jobs.html', error="No jobs found", request=request)

  try:
    site_enum = Site(site_name)
  except Exception:
    site_enum = Site.LINKEDIN
  jobs_res = parse_jobs_response(site_enum, data)
  if not jobs_res.is_success():
    return render_template('preview_jobs.html', error="Failed to parse jobs: " + jobs_res.error, request=request)
  jobs = jobs_res.data
  return render_template('preview_jobs.html', jobs=jobs, request=request)