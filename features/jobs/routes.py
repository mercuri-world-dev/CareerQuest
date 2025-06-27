from flask import Blueprint, render_template, request
import requests

from util.decorators import sb_login_required

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static')

@jobs_bp.route('/all_jobs')
@sb_login_required
def all_jobs():
    api_url = request.url_root.rstrip('/') + '/api/jobs'
    filters = request.args.to_dict()
    resp = requests.get(api_url, params=filters)
    jobs = resp if resp.status_code == 200 else []
    return render_template('all_jobs.html', jobs=jobs)