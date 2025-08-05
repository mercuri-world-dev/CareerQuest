from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from util.classes.result import Result
from util.models import Job, JobFactors, JobWithCompatibility, JobWithCompatibilityFactors, UserProfile

WEIGHTS = {
    "location_score": 0.3,
    "hours_score": 0.1,
    "work_mode_score": 0.2,
    "accommodations_score": 0.1,
    "qualifications_score": 0.3
}

# Public (should return Result or list[Result])

def calculate_jobs_compatibility(jobs: list[Job], user_profile: UserProfile) -> list[Result[JobWithCompatibility]]:
    jobs_with_compatibility: list[Result[JobWithCompatibility]] = []
    for job in jobs:
        compatibility_result = calculate_job_compatibility(job, user_profile)
        if compatibility_result.is_success():
            job_with_compatibility = JobWithCompatibility(
                **job.__dict__,
                compatibility_score=compatibility_result.data
            )
            jobs_with_compatibility.append(Result[JobWithCompatibility](success=True, data=job_with_compatibility))
        else:
            jobs_with_compatibility.append(Result[JobWithCompatibility](success=False, error=compatibility_result.error))
    return jobs_with_compatibility

def calculate_job_compatibility(job: Job, user_profile: UserProfile) -> Result[float]:
    data_res = calculate_job_compatibility_factors(job, user_profile)
    if not data_res.is_success():
        return Result[float](success=False, error=data_res.error)
    data = data_res.data
    total_score = _calculate_total_compatibility(data)
    return Result(success=True, data=total_score)

def calculate_job_compatibility_factors(job: Job, user_profile: UserProfile) -> Result[JobWithCompatibilityFactors]:
    try:
        user_prefs = (
            user_profile.remote_preference,
            user_profile.hybrid_preference,
            user_profile.in_person_preference
        )
        
        job_qualifications = ','.join(job.qualifications)

        location_score = _calculate_location_similarity(user_profile.location, job.location)
        hours_score = _calculate_hours_compatibility(user_profile.hours_per_week, job.weekly_hours)
        accommodations_score = _calculate_accommodations_match(user_profile.accommodations, job.accommodations)
        work_mode_score = _calculate_work_mode_compatibility(user_prefs, job.work_mode)
        qualifications_score = _calculate_qualifications_match(user_profile.educational_background, job_qualifications)

        overall_score: float = _calculate_total_compatibility_from_scores(
            JobFactors(
                location_score=location_score,
                hours_score=hours_score,
                work_mode_score=work_mode_score,
                accommodations_score=accommodations_score,
                qualifications_score=qualifications_score
            )
        )

        factors: JobFactors = JobFactors(
            location_score=location_score,
            hours_score=hours_score,
            work_mode_score=work_mode_score,
            accommodations_score=accommodations_score,
            qualifications_score=qualifications_score
        )

        job_with_factors = JobWithCompatibilityFactors(
            **job.__dict__,
            compatibility_score=overall_score,
            factors=factors
        )

        return Result[JobWithCompatibilityFactors](success=True, data=job_with_factors)
    except Exception as e:
        return Result[JobWithCompatibilityFactors](success=False, error=str(e))

# Private

def _calculate_location_similarity(user_location: str, job_location: str) -> float:
    """Calculate location similarity based on city/state/country match"""    
    user_loc_parts = user_location.lower().split(', ')
    job_loc_parts = job_location.lower().split(', ')
    
    matches = sum(p1 == p2 for p1, p2 in zip(user_loc_parts, job_loc_parts))
    return matches / max(len(user_loc_parts), len(job_loc_parts))

def _calculate_hours_compatibility(user_hours, job_hours):
    """Calculate hours compatibility"""
    if not user_hours or not job_hours:
        return 0.5 # Neutral score if data is missing
        
    # Simple formula - difference of more than 10 hours is considered incompatible
    difference = abs(user_hours - job_hours)
    return max(0, 1 - (difference / 10))

def _calculate_work_mode_compatibility(user_prefs, job_mode):
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

def _calculate_accommodations_match(user_accommodations, job_accommodations):
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
def _calculate_qualifications_match(user_qualifications, job_qualifications):
    try: 
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([user_qualifications, job_qualifications])
        qualification_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        qualification_score = 0.0
    return qualification_score if qualification_score else 0.0

def _calculate_total_compatibility_from_scores(scores: JobFactors) -> float:
    present = {k: v for k, v in scores.to_dict().items() if v is not None}
    present_weights = {k: w for k, w in WEIGHTS.items() if k in present}
    total_weight = sum(present_weights.values())
    if total_weight == 0:
        return 0.0
    normalized_weights = {k: w / total_weight for k, w in present_weights.items()}
    return sum(present[k] * normalized_weights[k] for k in present)

def _calculate_total_compatibility(job: JobWithCompatibilityFactors) -> float:
    return _calculate_total_compatibility_from_scores(
        JobFactors(
            location_score=job.factors.location_score,
            hours_score=job.factors.hours_score,
            work_mode_score=job.factors.work_mode_score,
            accommodations_score=job.factors.accommodations_score,
            qualifications_score=job.factors.qualifications_score
        )
    )






# Now becomes a thin wrapper that calls predict.py logic
