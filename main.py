from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import logout_user, login_required, current_user
from functools import wraps
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import db, User, Job
from util.decorators import role_required

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

# Helper functions for matching
def calculate_location_similarity(user_location, job_location):
    """Calculate location similarity based on city/state/country match"""
    if not user_location or not job_location:
        return 0.5 # Neutral score if data is missing
    
    user_loc_parts = user_location.lower().split(', ')
    job_loc_parts = job_location.lower().split(', ')
    
    matches = sum(p1 == p2 for p1, p2 in zip(user_loc_parts, job_loc_parts))
    return matches / max(len(user_loc_parts), len(job_loc_parts))

def calculate_hours_compatibility(user_hours, job_hours):
    """Calculate hours compatibility"""
    if not user_hours or not job_hours:
        return 0.5 # Neutral score if data is missing
        
    # Simple formula - difference of more than 10 hours is considered incompatible
    difference = abs(user_hours - job_hours)
    return max(0, 1 - (difference / 10))

def calculate_work_mode_compatibility(user_prefs, job_mode):
    """Calculate work mode compatibility"""
    if not job_mode:
        return 0.5 # Neutral score if data is missing
        
    remote_pref, hybrid_pref, in_person_pref = user_prefs
    
    if job_mode == 'remote' and remote_pref:
        return 1.0
    elif job_mode == 'hybrid' and hybrid_pref:
        return 1.0
    elif job_mode == 'in-person' and in_person_pref:
        return 1.0
    
    return 0.2 # Low compatibility but not zero

def calculate_accommodations_match(user_accommodations, job_accommodations):
    """Calculate accommodations match"""
    if not user_accommodations or not job_accommodations:
        return 1.0 # No specific accommodations needed
        
    # Convert all to lowercase for better matching
    user_acc = [acc.lower() for acc in user_accommodations]
    job_acc = [acc.lower() for acc in job_accommodations]
    
    # Count matches
    matches = sum(any(ua in ja for ja in job_acc) for ua in user_acc)
    return matches / len(user_acc) if user_acc else 1.0

@main_bp.route('/')
def index():
    # Don't just check is_authenticated - check if current_user is properly loaded
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        # Redirect to appropriate dashboard
        if current_user.has_role('admin'):
            return redirect(url_for('admin.index'))
        elif current_user.has_role('company'):
            return redirect(url_for('company.company_dashboard'))
        elif current_user.has_role('user'):
            return redirect(url_for('users.dashboard'))
    
    # If not authenticated or not properly loaded, show the index page
    return render_template('index.html')

@main_bp.route('/all_jobs')
@login_required
def all_jobs():
    jobs = Job.query.all()
    return render_template('all_jobs.html', jobs=jobs)

# API routes
@main_bp.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    # Strip leading zeros from user_id to match database ID
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
        
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(user.to_dict())

@main_bp.route('/api/current_user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())

@main_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    # Filter by status if provided
    status = request.args.get('status')
    if status:
        jobs = Job.query.filter_by(application_status=status).all()
    else:
        jobs = Job.query.all()
        
    return jsonify([job.to_dict() for job in jobs])

@main_bp.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    job = db.session.get(Job, job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    return jsonify(job.to_dict())

@main_bp.route('/api/matches', methods=['GET'])
@login_required
@role_required('user')
def get_matches_for_current_user():
    user = current_user
    return generate_matches_response(user)

@main_bp.route('/api/matches/<user_id>', methods=['GET'])
def get_matches(user_id):
    # Strip leading zeros from user_id to match database ID
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
        
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return generate_matches_response(user)

def generate_matches_response(user):
    # Calculate compatibility scores for each job
    try:
        jobs = Job.query.filter_by(application_status='Open').all()
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

@main_bp.route('/api/compatibility/<user_id>/<job_id>', methods=['GET'])
def get_compatibility(user_id, job_id):
    # Find the user and job
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
        
    user = User.query.get(user_id)
    job = db.session.get(Job, job_id)
    
    if not user or not job:
        return jsonify({"error": "User or job not found"}), 404
    
    try:    
        # Calculate compatibility factors
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
        
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([user_text.lower(), job_text.lower()])
            qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            qualification_score = 0.0
            
        # Calculate overall compatibility
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

@main_bp.route('/api/compatibility/current/<job_id>', methods=['GET'])
@login_required
def get_compatibility_current_user(job_id):
    user = current_user
    job = db.session.get(Job, job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    # Calculate compatibility factors
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
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([user_text.lower(), job_text.lower()])
        qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        qualification_score = 0.0
        
    # Calculate overall compatibility
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

# Add this debugging route to check authentication status
@main_bp.route('/debug_auth')
def debug_auth():
    debug_info = {
        "is_authenticated": current_user.is_authenticated,
        "is_active": current_user.is_active if hasattr(current_user, 'is_active') else "N/A",
        "is_anonymous": current_user.is_anonymous if hasattr(current_user, 'is_anonymous') else "N/A",
        "user_type": str(type(current_user)),
        "current_user_id": getattr(current_user, 'id', None)
    }
    return jsonify(debug_info)

@main_bp.route('/clear_session')
def clear_session():
    """Emergency route to clear session data if login/logout issues occur"""
    session.clear()
    logout_user()
    flash('Session cleared successfully')
    return redirect(url_for('main.index'))