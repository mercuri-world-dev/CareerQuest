from flask import Blueprint, render_template

from main.supabase_client import get_supabase
from db.models import Job
from util.decorators import sb_login_required

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static')

@jobs_bp.route('/all_jobs')
@sb_login_required
def all_jobs():
    supabase = get_supabase()
    jobs_data = supabase.table('jobs').select('*').execute()
    if not jobs_data.data:
        return render_template('all_jobs.html', jobs=[])
    jobs = [Job(**job) for job in jobs_data.data]
    return render_template('all_jobs.html', jobs=jobs)