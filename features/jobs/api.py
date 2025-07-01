from flask import Blueprint, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from features.debug.util.mock_data import MOCK_JOB, MOCK_USER_PROFILE
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
    print(f"Include compatibility: {include_compatibility}")
    # supabase = get_supabase()
    # query = supabase.table('jobs').select('*')
    # for field in JOB_FIELDS:
    #     value = request.args.get(field)
    #     if value is not None:
    #         if field in ['industry', 'qualifications', 'accommodations', 'application_materials']:
    #             values = [v.strip() for v in value.split(',') if v.strip()]
    #             if values:
    #                 query = query.contains(field, values)
    #         else:
    #             query = query.eq(field, value)
    # jobs_resp = query.execute()
    # jobs = jobs_resp.data if hasattr(jobs_resp, "data") else []
    jobs = [MOCK_JOB]
    if include_compatibility:
        # user_profile_resp = supabase.table('user_profiles').select('*').execute().data # Secure (RLS)
        
        # if not user_profile_resp:
        #     return jobs
        
        # user_profile = user_profile_resp[0] if isinstance(user_profile_resp, list) else user_profile_resp
        user_profile = MOCK_USER_PROFILE

        jobs_with_compatibility_result = scoring.calculate_jobs_compatibility(jobs, user_profile)

        if jobs_with_compatibility_result.is_success():
            jobs_with_compatibility = jobs_with_compatibility_result.data
        else:
            print(f"Error calculating job compatibility: {jobs_with_compatibility_result.error}")
            return jobs
        
        return jobs_with_compatibility
    return jobs

@jobs_api_bp.route('/jobs', methods=['GET'])
@sb_login_required
def get_jobs():
    include_compatibility = request.args.get('include_compatibility', 'false').lower() == 'true'
    return fetch_jobs(include_compatibility)
    
@jobs_api_bp.route('/job_click', methods=['POST'])
@sb_login_required
def job_click():
    print("Job click callback received")
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
        upsert_resp = supabase.table('job_clicks').upsert({
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
    # supabase = get_supabase()
    include_compatibility = request.args.get('include_compatibility', 'false').lower() == 'true'
    # try:
    #     job = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
    # except Exception as e:
    #     print(f"Error fetching job: {e}")
    #     return jsonify({"error": "Failed to fetch job"}), 500
    
    # if not job:
    #     return jsonify({"error": "Job not found"}), 404
    
    job = MOCK_JOB

    if include_compatibility:
        # user_profile_resp = supabase.table('user_profiles').select('*').limit(1).execute()
        # if not user_profile_resp or not getattr(user_profile_resp, 'data', None) or not user_profile_resp.data:
        #     return jsonify({"error": "User profile not found"}), 404
        
        # user_profile = user_profile_resp.data[0]
        user_profile = MOCK_USER_PROFILE
        job_with_compatibility = scoring.calculate_job_compatibility_factors(job, user_profile)
        # job_with_compatibility_result = scoring.calculate_job_compatibility_factors(job.data, user_profile)

        if job_with_compatibility:
            job.data.update({
                'compatibility_score': job_with_compatibility.get('compatibility_score', 0),
                'factors': job_with_compatibility.get('factors', [])
            })
            print(f"Job compatibility factors: {job.data.get('factors', [])}")
        else:
            print("No compatibility factors found for job")
            job.data['compatibility_score'] = 0
            job.data['factors'] = []

    # return jsonify(job.data)
    return jsonify(job)