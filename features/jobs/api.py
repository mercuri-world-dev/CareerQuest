from flask import Blueprint, jsonify, request

from features.jobs.util import job_scoring as scoring
from util.classes.result import Result
from util.models import Job, JobWithCompatibility, JobWithCompatibilityFactors, UserProfile
from services.supabase.supabase_client import get_supabase
from util.decorators import sb_login_required

JOB_FIELDS = [
    'id', 'provider', 'company_name', 'role_name', 'company_id', 'industry', 'weekly_hours', 'work_mode', 'location',
    'is_remote', 'description', 'job_type', 'application_materials', 'job_url', 'date_posted'
]

LIST_FIELDS = [
  'industry', 'application_materials'
]

jobs_api_bp = Blueprint('jobs_api', __name__)

def fetch_jobs() -> Result[list[Job]]:
    try:
        supabase = get_supabase()
        query = supabase.table('jobs').select('*')
        for field in JOB_FIELDS:
            value = request.args.get(field)
            if value is not None: 
                if field in LIST_FIELDS:
                    values = [v.strip() for v in value.split(',') if v.strip()]
                    if values:
                        query = query.contains(field, values)
                else:
                    query = query.eq(field, value)
        jobs_resp = query.execute()
        if not jobs_resp or not jobs_resp.data:
            print("No jobs found.")
            return Result(success=False, error="No jobs found", data=[])
        jobs_data = jobs_resp.data
        jobs = []
        for job_data in jobs_data:
            # Map the database fields to the Job class fields
            job_dict = {
                'id': job_data.get('id', ''),
                'provider': job_data.get('provider', 'MERCURI'),  # Default to MERCURI if not specified
                'company_name': job_data.get('company_name', ''),
                'role_name': job_data.get('role_name', ''),
                'company_id': job_data.get('company_id'),
                'industry': job_data.get('industry'),
                'job_url': job_data.get('application_link'),  # Map application_link to job_url
                'location': job_data.get('location'),
                'is_remote': job_data.get('work_mode') == 'remote' if job_data.get('work_mode') else None,
                'description': job_data.get('job_description'),  # Map job_description to description
                'job_type': job_data.get('job_type')
            }
            # Create Job object
            try:
                job = Job(**job_dict)
                jobs.append(job)
            except Exception as e:
                print(f"Error creating Job object: {e}")
                # Continue with next job if one fails
                continue
        return Result(success=True, data=jobs)
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return Result(success=False, error=str(e), data=[])

def fetch_jobs_with_compatibility() -> Result[list[Result[JobWithCompatibility]]]:
    try:
        supabase = get_supabase()
        jobs_res = fetch_jobs()
        if not jobs_res.is_success():
            return Result(success=False, error=jobs_res.error, data=[])
        jobs_data = jobs_res.data
        try:
            user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
            if not user_profile_resp or not user_profile_resp.data:
                print("User profile not found.")
                return Result(success=False, error="User profile not found", data=[])
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return Result(success=False, error="User profile not found", data=[])
        user_profile_dict = user_profile_resp.data[0]
        user_profile = UserProfile.from_supabase_dict(user_profile_dict)
        jobs_with_compat = scoring.calculate_jobs_compatibility(jobs_data, user_profile)
        return Result(success=True, data=jobs_with_compat)
    except Exception as e:
        print(f"Error fetching jobs with compatibility: {e}")
        return Result(success=False, error=str(e), data=[])

def fetch_jobs_with_compatibility_factors() -> Result[list[Result[JobWithCompatibilityFactors]]]:
    supabase = get_supabase()
    jobs_res = fetch_jobs()
    if not jobs_res.is_success():
        return Result(success=False, error=jobs_res.error, data=[])
    jobs_data = jobs_res.data
    try:
        user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
        if not user_profile_resp or not user_profile_resp.data:
            return Result(success=False, error="User profile not found", data=[])
        user_profile_dict = user_profile_resp.data[0]
        user_profile = UserProfile.from_supabase_dict(user_profile_dict)
        compat_results = [scoring.calculate_job_compatibility_factors(job, user_profile) for job in jobs_data]
        return Result(success=True, data=compat_results)
    except Exception as e:
        print(f"Error fetching user profile or calculating compatibility: {e}")
        return Result(success=False, error=str(e), data=[])

def fetch_job(job_id) -> Result[Job|None]:
    supabase = get_supabase()
    try:
        job_resp = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
    except Exception as e:
        print(f"Error fetching job: {e}")
        return Result(success=False, error=str(e))
    if not job_resp:
        print(f"Job with ID {job_id} not found.")
        return Result(success=False, error=f"Job with ID {job_id} not found.")
    try:
        job_data = job_resp.data
        if not job_data:
            print(f"Job with ID {job_id} not found.")
            return Result(success=False, error=f"Job with ID {job_id} not found.")
        
        # Map the database fields to the Job class fields
        job_dict = {
            'id': job_data.get('id', ''),
            'provider': job_data.get('provider', 'MERCURI'),  # Default to MERCURI if not specified
            'company_name': job_data.get('company_name', ''),
            'role_name': job_data.get('role_name', ''),
            'company_id': job_data.get('company_id'),
            'industry': job_data.get('industry'),
            'job_url': job_data.get('application_link'),  # Map application_link to job_url
            'location': job_data.get('location'),
            'is_remote': job_data.get('work_mode') == 'remote' if job_data.get('work_mode') else None,
            'description': job_data.get('job_description'),  # Map job_description to description
            'job_type': job_data.get('job_type')
        }
        
        # Create Job object
        job = Job(**job_dict)
    except Exception as e:
        print(f"Error processing job data: {e}")
        return Result(success=False, error=str(e))
    return Result(success=True, data=job)

def fetch_job_with_compatibility(job_id) -> Result[JobWithCompatibility|None]:
    job_result = fetch_job(job_id)
    if not job_result.is_success():
        return Result(success=False, data=None, error=job_result.error)
    job = job_result.data
    if job is None:
        return Result(success=False, data=None, error="Job not found")
    supabase = get_supabase()
    try:
        user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
        if not user_profile_resp or not user_profile_resp.data:
            print("User profile not found.")
            return Result(success=False, error="User profile not found.")
        user_profile_dict = user_profile_resp.data[0]
        user_profile = UserProfile.from_supabase_dict(user_profile_dict)
        compat_result = scoring.calculate_job_compatibility_factors(job, user_profile)
        if compat_result.is_success():
            job_with_factors = compat_result.data
            return Result(success=True, data=job_with_factors)
        else:
            print(f"Error calculating compatibility factors: {compat_result.error}")
            return Result(success=False, error=compat_result.error)
    except Exception as e:
        print(f"Error fetching user profile or calculating compatibility: {e}")
        return Result(success=False, error=str(e))

def fetch_job_with_compatibility_factors(job_id) -> Result[JobWithCompatibilityFactors|None]:
    job_result = fetch_job(job_id)
    if not job_result.is_success():
        return Result(success=False, error=job_result.error)
    if job_result.data is None:
        return Result(success=False, error="Job not found")
    job = job_result.data
    supabase = get_supabase()
    try:
        user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
        if not user_profile_resp or not user_profile_resp.data:
            print("User profile not found.")
            return Result(success=False, error="User profile not found.")
        user_profile_dict = user_profile_resp.data[0]
        user_profile = UserProfile.from_supabase_dict(user_profile_dict)
        compat_result = scoring.calculate_job_compatibility_factors(job, user_profile)
        if compat_result.is_success():
            job_with_factors = compat_result.data
            return Result(success=True, data=job_with_factors)
        else:
            print(f"Error calculating compatibility factors: {compat_result.error}")
            return Result(success=False, error=compat_result.error)
    except Exception as e:
        print(f"Error fetching user profile or calculating compatibility: {e}")
        return Result(success=False, error=str(e))

@jobs_api_bp.route('/jobs', methods=['GET'])
@sb_login_required
def get_jobs():
    include_compatibility = request.args.get('include_compatibility', 'false').lower() == 'true'
    include_factors = request.args.get('include_factors', 'false').lower() == 'true'
    if include_factors:
        result = fetch_jobs_with_compatibility_factors()
    else:
        result = fetch_jobs_with_compatibility() if include_compatibility else fetch_jobs()
    if result.is_success():
        return jsonify(result.data)
    else:
        return jsonify({'error': result.error}), 500

@jobs_api_bp.route('/job_click', methods=['POST']) 
@sb_login_required
def job_click():
    supabase = get_supabase()
    data = request.get_json()
    job_id = data.get('job_id')
    if not job_id:
        return jsonify({'error': 'Missing job_id'}), 400
    user_profile_resp = supabase.table('user_profiles').select('id').limit(1).execute()
    if not user_profile_resp:
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
    result = fetch_job(job_id)
    if not result.is_success():
        return jsonify({"error": result.error or "Job not found or failed to calculate compatibility"}), 404
    return jsonify(result.data)