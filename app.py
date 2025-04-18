# app.py - modifications to fix routing issues

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import uuid
from datetime import datetime, timedelta


# Import our models
from database import db, User, Job, Role, CompanyProfile

# Import Flask-Admin
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

# Initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///careerquest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db.init_app(app)

# Change this section in app.py
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add session configuration to ensure proper cleanup
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_USE_SIGNER'] = True

# After initializing the login_manager, add this function
@app.before_request
def clear_session_on_restart():
    """Force logout on server restart"""
    # Check if user is authenticated but session has a different server instance
    server_id = os.environ.get('SERVER_INSTANCE_ID', os.getpid())
    if 'server_id' not in session:
        # New session or server restarted
        session['server_id'] = server_id
        # If user was authenticated, log them out
        if current_user.is_authenticated:
            logout_user()
    elif session.get('server_id') != server_id:
        # Server restarted with existing session
        session['server_id'] = server_id
        if current_user.is_authenticated:
            logout_user()

@login_manager.user_loader
def load_user(user_id):
    try:
        user = db.session.get(User, int(user_id))
        if user is None:
            # User not found, return None to signal login_manager
            return None
        return user
    except Exception as e:
        print(f"Error loading user: {e}")
        return None


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or not hasattr(current_user, 'id'):
                return redirect(url_for('login'))
            
            if not any(current_user.has_role(role) for role in roles):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
                
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# Admin views with access control
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.has_role('admin'):
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Replace the current admin initialization with this
admin = Admin(
    app, 
    name='CareerQuest Admin', 
    template_mode='bootstrap3',
    index_view=MyAdminIndexView()
    # Don't specify base_template - let it use the default path
)
# Add admin views
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Role, db.session))
admin.add_view(SecureModelView(CompanyProfile, db.session))
admin.add_view(SecureModelView(Job, db.session))

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

@app.route('/')
def index():
    # Don't just check is_authenticated - check if current_user is properly loaded
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        # Redirect to appropriate dashboard
        if current_user.has_role('admin'):
            return redirect(url_for('admin.index'))
        elif current_user.has_role('company'):
            return redirect(url_for('company_dashboard'))
        elif current_user.has_role('user'):
            return redirect(url_for('dashboard'))
    
    # If not authenticated or not properly loaded, show the index page
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any potentially stale session data
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        logout_user()
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Redirect to appropriate dashboard based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
                
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    # After logout, explicitly redirect to the landing page
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Clear any potentially stale session data
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        logout_user()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        account_type = request.form.get('account_type', 'user')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Assign role based on account type
        role = Role.query.filter_by(name=account_type).first()
        if role:
            user.roles.append(role)
            print(f"Assigned role {role.name} to user {username}")
        else:
            print(f"Role {account_type} not found")
            
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/dashboard')
@login_required
@role_required('user')
def dashboard():
    return render_template('dashboard.html')

@app.route('/company_dashboard')
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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('user')
def profile():
    if request.method == 'POST':
        current_user.age_range = request.form.get('age_range')
        hours = request.form.get('hours_per_week')
        current_user.hours_per_week = int(hours) if hours else None
        current_user.location = request.form.get('location')
        current_user.educational_background = request.form.get('educational_background')
        current_user.remote_preference = request.form.get('remote_preference') == 'on'
        current_user.hybrid_preference = request.form.get('hybrid_preference') == 'on'
        current_user.in_person_preference = request.form.get('in_person_preference') == 'on'
        
        # Handle accommodations as a list
        accommodations = request.form.get('accommodations', '')
        accommodations_list = [item.strip() for item in accommodations.split(',') if item.strip()]
        current_user.set_accommodations_list(accommodations_list)
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
        
    return render_template('profile.html')

@app.route('/company_profile', methods=['GET', 'POST'])
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
            return redirect(url_for('company_dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating company profile: {e}")
            flash('There was an error updating your profile. Please try again.')
            
    return render_template('company_profile.html', company_profile=company_profile)

@app.route('/job_recommendations')
@login_required
@role_required('user')
def job_recommendations():
    return render_template('job_recommendations.html')

@app.route('/all_jobs')
@login_required
def all_jobs():
    jobs = Job.query.all()
    return render_template('all_jobs.html', jobs=jobs)

@app.route('/job_compatibility/<job_id>')
@login_required
@role_required('user')
def job_compatibility(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        flash('Job not found')
        return redirect(url_for('all_jobs'))
        
    return render_template('job_compatibility.html', job=job)

@app.route('/manage_jobs')
@login_required
@role_required('company')
def manage_jobs():
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company_profile'))
    
    jobs = []    
    try:
        jobs = Job.query.filter_by(company_profile_id=company_profile.id).all()
    except Exception as e:
        print(f"Error retrieving jobs: {e}")
        flash('There was an issue retrieving your jobs. Please try again later.')
        
    return render_template('manage_jobs.html', jobs=jobs)

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
@role_required('company')
def add_job():
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company_profile'))
        
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
            return redirect(url_for('manage_jobs'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return render_template('add_job.html')
        except Exception as e:
            db.session.rollback()
            print(f"Error adding job: {e}")
            flash('There was an error adding the job. Please try again.')
            
    return render_template('add_job.html')

@app.route('/edit_job/<job_id>', methods=['GET', 'POST'])
@login_required
@role_required('company')
def edit_job(job_id):
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company_profile'))
        
    job = db.session.get(Job, job_id)
    
    if not job or job.company_profile_id != company_profile.id:
        flash('Job not found or you do not have permission to edit it')
        return redirect(url_for('manage_jobs'))
        
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
            return redirect(url_for('manage_jobs'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return render_template('edit_job.html', job=job)
        except Exception as e:
            db.session.rollback()
            print(f"Error updating job: {e}")
            flash('There was an error updating the job. Please try again.')
            
    return render_template('edit_job.html', job=job)

@app.route('/delete_job/<job_id>', methods=['POST'])
@login_required
@role_required('company')
def delete_job(job_id):
    company_profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    
    if not company_profile:
        flash('Please complete your company profile first')
        return redirect(url_for('company_profile'))
        
    job = db.session.get(Job, job_id)
    
    if not job or job.company_profile_id != company_profile.id:
        flash('Job not found or you do not have permission to delete it')
        return redirect(url_for('manage_jobs'))
    
    try:    
        db.session.delete(job)
        db.session.commit()
        
        flash('Job deleted successfully!')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting job: {e}")
        flash('There was an error deleting the job. Please try again.')
        
    return redirect(url_for('manage_jobs'))

# API routes
@app.route('/api/users/<user_id>', methods=['GET'])
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

@app.route('/api/current_user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    # Filter by status if provided
    status = request.args.get('status')
    if status:
        jobs = Job.query.filter_by(application_status=status).all()
    else:
        jobs = Job.query.all()
        
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    job = db.session.get(Job, job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    return jsonify(job.to_dict())

@app.route('/api/matches', methods=['GET'])
@login_required
@role_required('user')
def get_matches_for_current_user():
    user = current_user
    return generate_matches_response(user)

@app.route('/api/matches/<user_id>', methods=['GET'])
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

@app.route('/api/compatibility/<user_id>/<job_id>', methods=['GET'])
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

@app.route('/api/compatibility/current/<job_id>', methods=['GET'])
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
@app.route('/debug_auth')
def debug_auth():
    debug_info = {
        "is_authenticated": current_user.is_authenticated,
        "is_active": current_user.is_active if hasattr(current_user, 'is_active') else "N/A",
        "is_anonymous": current_user.is_anonymous if hasattr(current_user, 'is_anonymous') else "N/A",
        "user_type": str(type(current_user)),
        "current_user_id": getattr(current_user, 'id', None)
    }
    return jsonify(debug_info)

@app.route('/clear_session')
def clear_session():
    """Emergency route to clear session data if login/logout issues occur"""
    session.clear()
    logout_user()
    flash('Session cleared successfully')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)