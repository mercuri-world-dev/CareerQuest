from flask import Blueprint, render_template

from services.api.jobspy import jobspy_fetch_jobs
from util.decorators import role_required

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
 
@admin_bp.route('/')
@role_required(['admin'])
def admin_dashboard():
    try:
        test_resp = jobspy_fetch_jobs(    
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri"],
            search_term="software engineer",
            google_search_term="software engineer jobs near San Francisco, CA since yesterday",
            location="San Francisco, CA",
            results_wanted=1,
            hours_old=72,
            country_indeed='USA'
        )
        print(test_resp)
        data = test_resp.data
        if not data:
            print("No jobs found or invalid response format")
            return render_template('admin_dashboard.html', error="No jobs found or invalid response format")
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return render_template('admin_dashboard.html', error="Failed to fetch jobs data: " + str(e))
    return render_template('admin_dashboard.html', response_items=data)
