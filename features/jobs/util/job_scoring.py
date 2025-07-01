from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from util.result import Result

def calculate_jobs_compatibility(jobs, user_profile) -> Result[list[dict]]:
    try:
        for job in jobs:
            job['compatibility_score'] = calculate_job_compatibility(job, user_profile)
    except Exception as e:
        print(f"Error calculating job compatibility: {e}")
        return Result(success=False, error=str(e))
    return Result(success=True, data=jobs)

def calculate_job_compatibility(job, user_profile):
    data = calculate_job_compatibility_factors(job, user_profile)

    if not data:
        return 0.0
    
    total_score = (
        data['location_score'] * 0.3 +
        data['hours_score'] * 0.1 +
        data['work_mode_score'] * 0.2 +
        data['accommodations_score'] * 0.1 +
        data['qualifications_score'] * 0.3
    )

    return total_score

def calculate_job_compatibility_factors(job, user_profile):
    # Extract user preferences
    user_location = user_profile.get('location')
    user_hours = int(user_profile.get('hours_per_week', 0))
    user_accommodations = user_profile.get('accommodations', [])
    user_prefs = (
        user_profile.get('remote_preference', False),
        user_profile.get('hybrid_preference', False),
        user_profile.get('in_person_preference', False)
    )
    user_qualifications = user_profile.get('educational_background')
    
    # Extract job details
    job_location = job.get('location')
    job_hours = int(job.get('weekly_hours'))
    job_accommodations = job.get('accommodations')
    job_mode = job.get('work_mode')
    job_qualifications = ','.join(job.get('qualifications'))

    # Calculate individual scores
    location_score = calculate_location_similarity(user_location, job_location)
    hours_score = calculate_hours_compatibility(user_hours, job_hours)
    work_mode_score = calculate_work_mode_compatibility(user_prefs, job_mode)
    accommodations_score = calculate_accommodations_match(user_accommodations, job_accommodations)
    qualifications_score = calculate_qualifications_match(user_qualifications, job_qualifications)
    
    return {
        'location_score': location_score,
        'hours_score': hours_score,
        'work_mode_score': work_mode_score,
        'accommodations_score': accommodations_score,
        'qualifications_score': qualifications_score
    }

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
    if not user_accommodations:
        return 1.0 # No specific accommodations needed
        
    # Convert all to lowercase for better matching
    user_acc = [acc.lower() for acc in user_accommodations]
    job_acc = [acc.lower() for acc in job_accommodations]
    
    # Count matches
    matches = sum(any(ua in ja for ja in job_acc) for ua in user_acc)
    return matches / len(user_acc) if user_acc else 1.0

# BETA FUNCTION, NOT PARTICULARLY ACCURATE
# TODO: Improve qualifications matching
def calculate_qualifications_match(user_qualifications, job_qualifications):
    try: 
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([user_qualifications, job_qualifications])
        qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        qualification_score = 0.0
    return qualification_score if qualification_score else 0.0