from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from db.models import Job
from main.supabase_client import get_supabase
from util.auth import fetch_user_role, get_access_token, get_current_user_id
from util.decorators import role_required, sb_login_required

CONTENT_MANAGER_GROUPS = ['admin', 'elevated_content_manager', 'content_manager']
ELEVATED_CONTENT_MANAGER_GROUPS = ['admin', 'elevated_content_manager']

cms_bp = Blueprint('cms', __name__, template_folder='templates', static_folder='static')

@cms_bp.route('/')
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def dashboard():
    return render_template('cms_dashboard.html')

@cms_bp.route('/manage-jobs')
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def manage_jobs():
    return render_template('cms_dashboard.html')
    # return render_template('manage_jobs.html')

@cms_bp.route('/add-job', methods=['GET', 'POST'])
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def add_job():
    supabase = get_supabase()
    current_user_id = get_current_user_id(supabase)
    if not current_user_id:
        flash('Failed to retrieve user id.', 'warning')
        return redirect(url_for('cms.dashboard'))

    companies_resp = supabase.table('company_profiles').select('*').execute()
    companies = companies_resp.data or []
    selected_company = None

    if request.method == 'POST':
        company_id = request.form.get('company_profile_id')
        selected_company = next((c for c in companies if str(c['id']) == str(company_id)), None)
        if not selected_company:
            flash('Please select a valid company.', 'warning')
            return render_template('add_job.html', companies=companies)
        try:
            application_status_response = request.form.get('application_status', 'Open')
            
            if application_status_response in ['Closed', 'Draft']:
                application_status = False
            else:
                application_status = True

            job = Job(
                company_profile_id=selected_company['id'],
                company_name=selected_company.get('company_name'),
                role_name=request.form.get('role_name'),
                weekly_hours=int(request.form.get('weekly_hours')) if request.form.get('weekly_hours') else None,
                work_mode=request.form.get('work_mode'),
                location=request.form.get('location'),
                job_type=request.form.get('job_type'),
                job_description=request.form.get('job_description'),
                application_link=request.form.get('application_link'),
                application_status=application_status
            )
            # Handle lists
            industry = request.form.get('industry', '')
            industry_list = [item.strip() for item in industry.split(',') if item.strip()]
            job.set_industry_list(industry_list)
            
            qualifications = request.form.get('qualifications', '')
            qualifications_list = [item.strip() for item in qualifications.split(',') if item.strip()]
            job.set_qualifications_list(qualifications_list)
            
            accommodations = request.form.get('accommodations', '')
            accommodations_list = [item.strip() for item in accommodations.split(',') if item.strip()]
            job.set_accommodations_list(accommodations_list)
            
            application_materials = request.form.get('application_materials', '')
            materials_list = [item.strip() for item in application_materials.split(',') if item.strip()]
            job.set_application_materials_list(materials_list)
            
            # Handle dates
            if request.form.get('application_period_start'):
                job.application_period_start = datetime.strptime(
                    request.form.get('application_period_start'), '%Y-%m-%d'
                )
            if request.form.get('application_period_end'):
                job.application_period_end = datetime.strptime(
                    request.form.get('application_period_end'), '%Y-%m-%d'
                )

            supabase.table('jobs').insert(job.to_dict()).execute()
            
            flash('Job added successfully!', 'message')
            return redirect(url_for('cms.manage_jobs'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'warning')
            return render_template('add_job.html', companies=companies)
        except Exception as e:
            print(f"Error adding job: {e}")
            flash('There was an error adding the job. Please try again.', 'error')
            return render_template('add_job.html', companies=companies)
    return render_template('add_job.html', companies=companies)

@cms_bp.route('/add-company', methods=['GET', 'POST'])
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def add_company():
    supabase = get_supabase()
    current_user_id = get_current_user_id(supabase)
    if not current_user_id:
        flash('Failed to retrieve user id.', 'warning')
        return redirect(url_for('cms.dashboard'))
    
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        industry = request.form.get('industry', '')
        industry_list = [item.strip() for item in industry.split(',') if item.strip()]
        description = request.form.get('description')
        website = request.form.get('website')
        location = request.form.get('location')
        if not company_name:
            flash('Company name is required.', 'warning')
            return render_template('add_company.html')
        try:
            company_data = {
                'company_name': company_name,
                'industry': industry_list,
                'description': description,
                'website': website,
                'location': location,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            resp = supabase.table('company_profiles').insert(company_data).execute()
            print(f"Company insert response: {resp}")
            flash('Company profile added successfully!', 'message')
            return redirect(url_for('cms.dashboard'))
        except Exception as e:
            print(f"Error adding company: {e}")
            flash('There was an error adding the company. Please try again.', 'error')
            return render_template('add_company.html')
    return render_template('add_company.html')