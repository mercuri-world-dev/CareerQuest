
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