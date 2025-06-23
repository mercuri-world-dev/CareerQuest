from datetime import datetime
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from database import CompanyProfile, Job, db
from util.decorators import role_required

company_bp = Blueprint('company', __name__, template_folder='templates', static_folder='static', static_url_path='/static/company')

@company_bp.route('/company_dashboard')
@login_required
@role_required('company')
def company_dashboard():
    # Get company profile or create if it doesn't exist
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    # Initialize jobs as an empty list
    jobs = []
    
    # Get jobs posted by this company if the profile exists
    if company_profile:
        try:
            jobs = Job.query.filter_by(company_profile_id=company_profile.id).all()
        except Exception as e:
            # In case of database errors, log it but don't crash
            print(f"Error retrieving jobs: {e}")
            flash('There was an issue retrieving your jobs. Please try again later.')
        
    return render_template('company_dashboard.html', company_profile=company_profile, jobs=jobs)

@company_bp.route('/company_profile', methods=['GET', 'POST'])
@login_required
@role_required('company')
def company_profile():
    # Get or create company profile
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        company_profile = CompanyProfile(user_id=current_user.id, company_name='')
        db.session.add(company_profile)
        
    if request.method == 'POST':
        company_profile.company_name = request.form.get('company_name')
        company_profile.location = request.form.get('location')
        company_profile.description = request.form.get('description')
        company_profile.website = request.form.get('website')
        
        # Handle industry as a list
        industry = request.form.get('industry', '')
        industry_list = [item.strip() for item in industry.split(',') if item.strip()]
        company_profile.set_industry_list(industry_list)
        
        try:
            db.session.commit()
            flash('Company profile updated successfully!')
            return redirect(url_for('company.company_dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating company profile: {e}")
            flash('There was an error updating your profile. Please try again.')
            
    return render_template('company_profile.html', company_profile=company_profile)

@company_bp.route('/manage_jobs')
@login_required
@role_required('company')
def manage_jobs():
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company.company_profile'))
    
    jobs = []    
    try:
        jobs = Job.query.filter_by(company_profile_id=company_profile.id).all()
    except Exception as e:
        print(f"Error retrieving jobs: {e}")
        flash('There was an issue retrieving your jobs. Please try again later.')
        
    return render_template('manage_jobs.html', jobs=jobs)

@company_bp.route('/add_job', methods=['GET', 'POST'])
@login_required
@role_required('company')
def add_job():
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company.company_profile'))
        
    if request.method == 'POST':
        # Generate a unique ID for the job
        job_id = f"job{uuid.uuid4().hex[:6]}"
        
        try:
            # Create new job
            job = Job(
                id=job_id,
                company_profile_id=company_profile.id,
                company_name=company_profile.company_name,
                role_name=request.form.get('role_name'),
                weekly_hours=int(request.form.get('weekly_hours')) if request.form.get('weekly_hours') else None,
                work_mode=request.form.get('work_mode'),
                location=request.form.get('location'),
                job_type=request.form.get('job_type'),
                job_description=request.form.get('job_description'),
                application_link=request.form.get('application_link'),
                application_status=request.form.get('application_status', 'Open')
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
                
            db.session.add(job)
            db.session.commit()
            
            flash('Job added successfully!')
            return redirect(url_for('company.manage_jobs'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return render_template('add_job.html')
        except Exception as e:
            db.session.rollback()
            print(f"Error adding job: {e}")
            flash('There was an error adding the job. Please try again.')
            
    return render_template('add_job.html')

@company_bp.route('/edit_job/<job_id>', methods=['GET', 'POST'])
@login_required
@role_required('company')
def edit_job(job_id):
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company.company_profile'))
        
    job = db.session.get(Job, job_id)
    
    if not job or job.company_profile_id != company_profile.id:
        flash('Job not found or you do not have permission to edit it')
        return redirect(url_for('company.manage_jobs'))
        
    if request.method == 'POST':
        try:
            job.role_name = request.form.get('role_name')
            job.weekly_hours = int(request.form.get('weekly_hours')) if request.form.get('weekly_hours') else None
            job.work_mode = request.form.get('work_mode')
            job.location = request.form.get('location')
            job.job_type = request.form.get('job_type')
            job.job_description = request.form.get('job_description')
            job.application_link = request.form.get('application_link')
            job.application_status = request.form.get('application_status', 'Open')
            
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
                
            db.session.commit()
            
            flash('Job updated successfully!')
            return redirect(url_for('company.manage_jobs'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return render_template('edit_job.html', job=job)
        except Exception as e:
            db.session.rollback()
            print(f"Error updating job: {e}")
            flash('There was an error updating the job. Please try again.')
            
    return render_template('edit_job.html', job=job)

@company_bp.route('/delete_job/<job_id>', methods=['POST'])
@login_required
@role_required('company')
def delete_job(job_id):
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company.company_profile'))
        
    job = db.session.get(Job, job_id)
    
    if not job or job.company_profile_id != company_profile.id:
        flash('Job not found or you do not have permission to delete it')
        return redirect(url_for('company.manage_jobs'))
    
    try:    
        db.session.delete(job)
        db.session.commit()
        
        flash('Job deleted successfully!')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting job: {e}")
        flash('There was an error deleting the job. Please try again.')
        
    return redirect(url_for('company.manage_jobs'))