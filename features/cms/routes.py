from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime, timezone
import json

from services.supabase.supabase_client import get_supabase
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
    supabase = get_supabase()
    # Get all jobs for companies owned by the current user
    companies_resp = supabase.table('company_profiles').select('id').execute()
    company_ids = [c['id'] for c in (companies_resp.data or [])]
    jobs_resp = supabase.table('jobs').select('*').in_('company_profile_id', company_ids).execute()
    jobs = jobs_resp.data or []
    return render_template('manage_jobs.html', jobs=jobs)

@cms_bp.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def edit_job(job_id):
    supabase = get_supabase()
    job_resp = supabase.table('jobs').select('*').eq('id', job_id).single().execute()
    job = job_resp.data
    if not job:
        flash('Job not found.', 'warning')
        return redirect(url_for('cms.manage_jobs'))
    if request.method == 'POST':
        # Parse form data
        provided_id = request.form.get('provided_id')
        provider = request.form.get('provider')
        company_name = request.form.get('company_name')
        role_name = request.form.get('role_name')
        industry = request.form.get('industry', '')
        industry_list = [item.strip() for item in industry.split(',') if item.strip()]
        job_url = request.form.get('job_url')
        location = request.form.get('location')
        is_remote = request.form.get('is_remote') == 'on'
        description = request.form.get('description')
        job_type = request.form.get('job_type')
        interval = request.form.get('interval')
        min_amount = request.form.get('min_amount')
        max_amount = request.form.get('max_amount')
        currency = request.form.get('currency')
        salary_source = request.form.get('salary_source')
        date_posted_str = request.form.get('date_posted')
        date_posted = datetime.strptime(date_posted_str, '%Y-%m-%d').date() if date_posted_str else None
        emails_str = request.form.get('emails', '')
        emails_list = [email.strip() for email in emails_str.split(',') if email.strip()]
        
        # Site-specific fields
        job_level = request.form.get('job_level')
        company_industry = request.form.get('company_industry')
        skills = request.form.get('skills')
        experience_range = request.form.get('experience_range')
        additional_fields_str = request.form.get('additional_fields')
        additional_fields = None
        if additional_fields_str:
            try:
                additional_fields = json.loads(additional_fields_str)
            except:
                additional_fields = None
        
        update_data = {
            'provided_id': provided_id,
            'provider': provider,
            'company_name': company_name,
            'role_name': role_name,
            'industry': industry_list,
            'job_url': job_url,
            'location': location,
            'is_remote': is_remote,
            'description': description,
            'job_type': job_type,
            'interval': interval,
            'min_amount': float(min_amount) if min_amount else None,
            'max_amount': float(max_amount) if max_amount else None,
            'currency': currency,
            'salary_source': salary_source,
            'date_posted': date_posted.isoformat() if date_posted else None,
            'emails': emails_list,
            'job_level': job_level,
            'skills': skills,
            'experience_range': experience_range,
            'additional_fields': additional_fields,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        supabase.table('jobs').update(update_data).eq('id', job_id).execute()
        flash('Job updated successfully!', 'message')
        return redirect(url_for('cms.manage_jobs'))
    return render_template('add_or_edit_job.html', job=job)

@cms_bp.route('/add-job', methods=['GET', 'POST'])
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def add_job():
    supabase = get_supabase()

    companies_resp = supabase.table('company_profiles').select('*').execute()
    companies = companies_resp.data or []
    selected_company = None

    if request.method == 'POST':
        company_id = request.form.get('company_profile_id')
        selected_company = next((c for c in companies if str(c['id']) == str(company_id)), None)
        if not selected_company:
            flash('Please select a valid company.', 'warning')
            return render_template('add_or_edit_job.html', companies=companies, job=None)
        
        # Parse form data
        provided_id = request.form.get('provided_id')
        provider = request.form.get('provider')
        role_name = request.form.get('role_name')
        industry = request.form.get('industry', '')
        industry_list = [item.strip() for item in industry.split(',') if item.strip()]
        job_url = request.form.get('job_url')
        location = request.form.get('location')
        is_remote = request.form.get('is_remote') == 'on'
        description = request.form.get('description')
        job_type = request.form.get('job_type')
        interval = request.form.get('interval')
        min_amount = request.form.get('min_amount')
        max_amount = request.form.get('max_amount')
        currency = request.form.get('currency')
        salary_source = request.form.get('salary_source')
        date_posted_str = request.form.get('date_posted')
        date_posted = datetime.strptime(date_posted_str, '%Y-%m-%d').date() if date_posted_str else None
        emails_str = request.form.get('emails', '')
        emails_list = [email.strip() for email in emails_str.split(',') if email.strip()]
        
        # Site-specific fields
        job_level = request.form.get('job_level')
        company_industry = request.form.get('company_industry')
        skills = request.form.get('skills')
        experience_range = request.form.get('experience_range')
        additional_fields_str = request.form.get('additional_fields')
        additional_fields = None
        if additional_fields_str:
            try:
                additional_fields = json.loads(additional_fields_str)
            except:
                additional_fields = None
        
        job_data = {
            'provided_id': provided_id,
            'provider': provider,
            'company_name': selected_company['company_name'],
            'company_profile_id': selected_company['id'],
            'role_name': role_name,
            'industry': industry_list,
            'job_url': job_url,
            'location': location,
            'is_remote': is_remote,
            'description': description,
            'job_type': job_type,
            'interval': interval,
            'min_amount': float(min_amount) if min_amount else None,
            'max_amount': float(max_amount) if max_amount else None,
            'currency': currency,
            'salary_source': salary_source,
            'date_posted': date_posted.isoformat() if date_posted else None,
            'emails': emails_list,
            'job_level': job_level,
            'company_industry': company_industry,
            'skills': skills,
            'experience_range': experience_range,
            'additional_fields': additional_fields,
        }

        supabase.table('jobs').insert(job_data).execute()
        flash('Job added successfully!', 'message')
        return redirect(url_for('cms.manage_jobs'))
    return render_template('add_or_edit_job.html', companies=companies, job=None)

@cms_bp.route('/manage-companies')
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def manage_companies():
    supabase = get_supabase()
    companies_resp = supabase.table('company_profiles').select('*').execute()
    companies = companies_resp.data or []
    return render_template('manage_companies.html', companies=companies)

@cms_bp.route('/edit-company/<int:company_id>', methods=['GET', 'POST'])
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def edit_company(company_id):
    supabase = get_supabase()
    company_resp = supabase.table('company_profiles').select('*').eq('id', company_id).single().execute()
    company = company_resp.data
    if not company:
        flash('Company not found.', 'warning')
        return redirect(url_for('cms.manage_companies'))
    if request.method == 'POST':
        update_data = {
            'company_name': request.form.get('company_name'),
            'industry': [item.strip() for item in request.form.get('industry', '').split(',') if item.strip()],
            'description': request.form.get('description'),
            'website': request.form.get('website'),
            'location': request.form.get('location'),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        supabase.table('company_profiles').update(update_data).eq('id', company_id).execute()
        flash('Company updated successfully!', 'message')
        return redirect(url_for('cms.manage_companies'))
    return render_template('edit_company.html', company=company)

@cms_bp.route('/add-company', methods=['GET', 'POST'])
@sb_login_required
@role_required(CONTENT_MANAGER_GROUPS)
def add_company():
    supabase = get_supabase()
    
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
            }
            resp = supabase.table('company_profiles').insert(company_data).execute()
            flash('Company profile added successfully!', 'message')
            return redirect(url_for('cms.dashboard'))
        except Exception as e:
            print(f"Error adding company: {e}")
            flash('There was an error adding the company. Please try again.', 'error')
            return render_template('add_company.html')
    return render_template('add_company.html')