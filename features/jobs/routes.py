from flask import Blueprint, render_template
from flask_login import login_required

from database import Job

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static')

@jobs_bp.route('/all_jobs')
@login_required
def all_jobs():
    jobs = Job.query.all()
    return render_template('all_jobs.html', jobs=jobs)