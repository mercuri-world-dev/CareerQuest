from flask import Blueprint, render_template
from flask_login import login_required

from database import Job
from util.decorators import sb_login_required

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static')

@jobs_bp.route('/all_jobs')
@sb_login_required
def all_jobs():
    jobs = Job.query.all()
    return render_template('all_jobs.html', jobs=jobs)