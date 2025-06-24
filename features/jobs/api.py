from flask import Blueprint, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import User
from features.jobs.util.job_scoring import calculate_accommodations_match, calculate_hours_compatibility, calculate_location_similarity, calculate_work_mode_compatibility
from main.supabase_client import get_supabase
from util.auth import get_supabase_user
from util.decorators import role_required, sb_login_required

jobs_api_bp = Blueprint('jobs_api', __name__)

# API routes
@jobs_api_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    supabase = get_supabase()
    try:
      user_id = int(user_id)
    except ValueError:
      return jsonify({"error": "Invalid user ID"}), 400
    
    user = supabase.table('users').select('*').eq('id', user_id).single().execute()
    
    if not user:
      return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict())

@jobs_api_bp.route('/current_user', methods=['GET'])
@sb_login_required
def get_current_user():
    supabase_user = get_supabase_user()
    if not supabase_user:
        return jsonify({"error": "User not authenticated"}), 401
    supabase = get_supabase()
    user = supabase.table('users').select('*').eq('id', supabase_user.id).single().execute()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@jobs_api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    supabase = get_supabase()
    status = request.args.get('status')
    if status:
        jobs = supabase.table('jobs').select('*').eq('application_status', status).execute()
    else:
        jobs = supabase.table('jobs').select('*').execute()
        
    return jsonify([job.to_dict() for job in jobs])

@jobs_api_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    supabase = get_supabase()
    job = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    return jsonify(job.to_dict())

@jobs_api_bp.route('/matches', methods=['GET'])
@sb_login_required
@role_required('user')
def get_matches_for_current_user():
    supabase_user = get_supabase_user()
    if not supabase_user:
        return jsonify({"error": "User not authenticated"}), 401
    supabase = get_supabase()
    user = supabase.table('users').select('*').eq('id', supabase_user.id).single().execute()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return generate_matches_response(user)

@jobs_api_bp.route('/matches/<user_id>', methods=['GET'])
def get_matches(user_id):
    supabase = get_supabase()
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
        
    user = supabase.table('users').select('*').eq('id', user_id).single().execute()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return generate_matches_response(user)

def generate_matches_response(user: User):
    # Calculate compatibility scores for each job
    try:
        jobs = get_supabase().table('jobs').select('*').execute()
        scores = []
        
        for job in jobs:
            # Calculate various compatibility factors
            location_score = calculate_location_similarity(user.location, job.location)
            hours_score = calculate_hours_compatibility(user.hours_per_week, job.weekly_hours)
            work_mode_score = calculate_work_mode_compatibility(
                [user.remote_preference, user.hybrid_preference, user.in_person_preference],
                job.work_mode
            )
            
            accommodations_score = calculate_accommodations_match(
                user.get_accommodations_list(),
                job.get_accommodations_list()
            )
            
            # Calculate text similarity between user background and job qualifications
            user_text = user.educational_background or ""
            job_text = ' '.join(job.get_qualifications_list())
            
            # Use TF-IDF for text matching
            try:
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform([user_text.lower(), job_text.lower()])
                qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            except:
                qualification_score = 0.0
                
            # Weighted average of all scores
            total_score = (
                location_score * 0.3 +
                hours_score * 0.1 +
                work_mode_score * 0.2 +
                accommodations_score * 0.1 +
                qualification_score * 0.3
            )
            
            job_dict = job.to_dict()
            scores.append({
                "job_id": job.id,
                "company_name": job.company_name,
                "role_name": job.role_name,
                "industry": job.get_industry_list(),
                "weekly_hours": job.weekly_hours,
                "work_mode": job.work_mode,
                "location": job.location,
                "qualifications": job.get_qualifications_list(),
                "compatibility_score": total_score,
                "factors": {
                    "location": location_score,
                    "hours": hours_score,
                    "work_mode": work_mode_score,
                    "accommodations": accommodations_score,
                    "qualifications": qualification_score
                }
            })
            
        # Sort jobs by compatibility score
        sorted_scores = sorted(scores, key=lambda x: x['compatibility_score'], reverse=True)
        
        return jsonify({
            "user_id": str(user.id).zfill(10),
            "matches": sorted_scores
        })
    except Exception as e:
        print(f"Error generating matches: {e}")
        return jsonify({
            "user_id": str(user.id).zfill(10),
            "matches": [],
            "error": "There was an error generating matches. Please try again later."
        }), 500

@jobs_api_bp.route('/compatibility/<user_id>/<job_id>', methods=['GET'])
def get_compatibility(user_id, job_id):
    supabase = get_supabase()
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
        
    user = supabase.table('users').select('*').eq('id', user_id).single().execute()
    job = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
    
    if not user or not job:
        return jsonify({"error": "User or job not found"}), 404
    
    try:    
        location_score = calculate_location_similarity(user.location, job.location)
        hours_score = calculate_hours_compatibility(user.hours_per_week, job.weekly_hours)
        work_mode_score = calculate_work_mode_compatibility(
            [user.remote_preference, user.hybrid_preference, user.in_person_preference],
            job.work_mode
        )
        
        accommodations_score = calculate_accommodations_match(
            user.get_accommodations_list(),
            job.get_accommodations_list()
        )
        
        user_text = user.educational_background or ""
        job_text = ' '.join(job.get_qualifications_list())
        
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([user_text.lower(), job_text.lower()])
            qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            qualification_score = 0.0
            
        total_score = (
            location_score * 0.3 +
            hours_score * 0.1 +
            work_mode_score * 0.2 +
            accommodations_score * 0.1 +
            qualification_score * 0.3
        )
        
        job_dict = job.to_dict()
        job_dict.update({
            "overall_compatibility": total_score,
            "factors": {
                "location": location_score,
                "hours": hours_score,
                "work_mode": work_mode_score,
                "accommodations": accommodations_score,
                "qualifications": qualification_score
            }
        })
        
        return jsonify(job_dict)
    except Exception as e:
        print(f"Error calculating compatibility: {e}")
        return jsonify({"error": "There was an error calculating compatibility. Please try again later."}), 500

@jobs_api_bp.route('/compatibility/current/<job_id>', methods=['GET'])
@sb_login_required
def get_compatibility_current_user(job_id):
    supabase_user = get_supabase_user()
    if not supabase_user:
        return jsonify({"error": "User not authenticated"}), 401
    supabase = get_supabase()
    user = supabase.table('users').select('*').eq('id', supabase_user.id).single().execute()
    if not user:
        return jsonify({"error": "User not found"}), 404
    job = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    location_score = calculate_location_similarity(user.location, job.location)
    hours_score = calculate_hours_compatibility(user.hours_per_week, job.weekly_hours)
    work_mode_score = calculate_work_mode_compatibility(
        [user.remote_preference, user.hybrid_preference, user.in_person_preference],
        job.work_mode
    )
    
    accommodations_score = calculate_accommodations_match(
        user.get_accommodations_list(),
        job.get_accommodations_list()
    )
    
    user_text = user.educational_background or ""
    job_text = ' '.join(job.get_qualifications_list())
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([user_text.lower(), job_text.lower()])
        qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        qualification_score = 0.0
        
    total_score = (
        location_score * 0.3 +
        hours_score * 0.1 +
        work_mode_score * 0.2 +
        accommodations_score * 0.1 +
        qualification_score * 0.3
    )
    
    job_dict = job.to_dict()
    job_dict.update({
        "overall_compatibility": total_score,
        "factors": {
            "location": location_score,
            "hours": hours_score,
            "work_mode": work_mode_score,
            "accommodations": accommodations_score,
            "qualifications": qualification_score
        }
    })
    
    return jsonify(job_dict)