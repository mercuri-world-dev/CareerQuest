from flask import Blueprint, jsonify, request
from features.jobs.util import job_scoring as scoring
from main.supabase_client import get_supabase
from util.decorators import sb_login_required

JOB_FIELDS = [
    'id', 'company_profile_id', 'company_name', 'role_name', 'industry', 'weekly_hours', 'work_mode', 'location',
    'qualifications', 'accommodations', 'application_period_start', 'application_period_end', 'application_status',
    'job_type', 'application_materials', 'job_description', 'application_link', 'created_at', 'updated_at'
]

jobs_api_bp = Blueprint('jobs_api', __name__)

def fetch_jobs(include_compatibility=False):
    supabase = get_supabase()
    query = supabase.table('jobs').select('*')
    for field in JOB_FIELDS:
        value = request.args.get(field)
        if value is not None:
            if field in ['industry', 'qualifications', 'accommodations', 'application_materials']:
                values = [v.strip() for v in value.split(',') if v.strip()]
                if values:
                    query = query.contains(field, values)
            else:
                query = query.eq(field, value)
    jobs_resp = query.execute()
    jobs = jobs_resp.data if hasattr(jobs_resp, "data") else []
    if include_compatibility:
        user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
        if not user_profile_resp or not getattr(user_profile_resp, 'data', None) or not user_profile_resp.data:
            return jobs
        user_profile = user_profile_resp.data[0]
        result = scoring.calculate_jobs_compatibility(jobs, user_profile)
        if result.is_success():
            # Add factors for each job
            for job in jobs:
                factors = scoring.calculate_job_compatibility_factors(job, user_profile).get('factors', [])
                job['factors'] = factors
            return jobs
        else:
            print(f"Error calculating job compatibility: {result.error}")
            return jobs
    return jobs

def fetch_job(job_id, include_compatibility=True):
    supabase = get_supabase()
    try:
        job_resp = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
        job = job_resp.data if hasattr(job_resp, 'data') else job_resp
    except Exception as e:
        print(f"Error fetching job: {e}")
        return None
    if not job:
        return None
    if include_compatibility:
        try:
            user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return job
        if not user_profile_resp:
            return job
        user_profile = user_profile_resp.data[0]
        factors = scoring.calculate_job_compatibility_factors(job, user_profile).get('factors_list', [])
        print(f"Compatibility factors for job {job_id}: {factors}")
        job['factors'] = factors
    return job

@jobs_api_bp.route('/jobs', methods=['GET'])
@sb_login_required
def get_jobs():
    include_compatibility = request.args.get('include_compatibility', 'false').lower() == 'true'
    jobs = fetch_jobs(include_compatibility)
    return jsonify(jobs)

@jobs_api_bp.route('/job_click', methods=['POST'])
@sb_login_required
def job_click():
    supabase = get_supabase()
    data = request.get_json()
    job_id = data.get('job_id')
    if not job_id:
        return jsonify({'error': 'Missing job_id'}), 400
    user_profile_resp = supabase.table('user_profiles').select('id').limit(1).execute()
    if not user_profile_resp or not getattr(user_profile_resp, 'data', None) or not user_profile_resp.data:
        return jsonify({'error': 'User profile not found'}), 404
    user_profile_id = user_profile_resp.data[0]['id']
    try:
        supabase.table('job_clicks').upsert({
            'job_id': job_id,
            'user_profile_id': user_profile_id
        }, on_conflict='job_id, user_profile_id').execute()
    except Exception as e:
        print(f"Error upserting job click: {e}")
        return jsonify({'error': 'Failed to record job click'}), 500
    return jsonify({'success': True})

@jobs_api_bp.route('/jobs/<job_id>', methods=['GET'])
@sb_login_required
def get_job(job_id):
    job = fetch_job(job_id)
    if not job:
        return jsonify({"error": "Job not found or failed to calculate compatibility"}), 404
    return jsonify(job)