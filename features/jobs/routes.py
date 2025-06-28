from flask import Blueprint, render_template, request
from util.decorators import sb_login_required
from main.supabase_client import get_supabase

jobs_bp = Blueprint('jobs', __name__, template_folder='templates', static_folder='static')

@jobs_bp.route('/all_jobs')
@sb_login_required
def all_jobs():
    supabase = get_supabase()
    job_fields = [
        'id', 'company_profile_id', 'company_name', 'role_name', 'industry', 'weekly_hours', 'work_mode', 'location',
        'qualifications', 'accommodations', 'application_period_start', 'application_period_end', 'application_status',
        'job_type', 'application_materials', 'job_description', 'application_link', 'created_at', 'updated_at'
    ]
    query = supabase.table('jobs').select('*')
    for field in job_fields:
        value = request.args.get(field)
        if value is not None:
            if field in ['industry', 'qualifications', 'accommodations', 'application_materials']:
                values = [v.strip() for v in value.split(',') if v.strip()]
                if values:
                    query = query.contains(field, values)
            else:
                query = query.eq(field, value)
    jobs = query.execute()
    jobs_resp = query.execute()
    jobs = jobs_resp.data if hasattr(jobs_resp, "data") else []
    return render_template('all_jobs.html', jobs=jobs)