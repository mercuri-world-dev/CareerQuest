# database.py - modifications

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json
from datetime import datetime

db = SQLAlchemy()

# Role model for role-based access control
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

# User-Role association table
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Role relationship
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    
    # Profile information
    age_range = db.Column(db.String(20))
    hours_per_week = db.Column(db.Integer)
    location = db.Column(db.String(100))
    accommodations = db.Column(db.Text) # Stored as JSON
    educational_background = db.Column(db.Text)
    remote_preference = db.Column(db.Boolean, default=False)
    hybrid_preference = db.Column(db.Boolean, default=False)
    in_person_preference = db.Column(db.Boolean, default=False)
    
    # Company relationship (if user is a company)
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_accommodations_list(self):
        if self.accommodations:
            return json.loads(self.accommodations)
        return []

    def set_accommodations_list(self, accommodations_list):
        self.accommodations = json.dumps(accommodations_list)
        
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def to_dict(self):
        return {
            'uid': str(self.id).zfill(10),
            'username': self.username,
            'email': self.email,
            'age_range': self.age_range,
            'hours_per_week': self.hours_per_week,
            'location': self.location,
            'accommodations': self.get_accommodations_list(),
            'educational_background': self.educational_background,
            'remote_preference': self.remote_preference,
            'hybrid_preference': self.hybrid_preference,
            'in_person_preference': self.in_person_preference
        }

# Company Profile model
class CompanyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.Text)  # Stored as JSON
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    location = db.Column(db.String(100))
    
    # Jobs relationship
    jobs = db.relationship('Job', backref='company', lazy='dynamic')
    
    def get_industry_list(self):
        return json.loads(self.industry) if self.industry else []
        
    def set_industry_list(self, industry_list):
        self.industry = json.dumps(industry_list)
        
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'industry': self.get_industry_list(),
            'description': self.description,
            'website': self.website,
            'location': self.location
        }

class Job(db.Model):
    """Job model for job listings"""
    id = db.Column(db.String(20), primary_key=True)
    company_profile_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'))
    company_name = db.Column(db.String(100), nullable=False)
    role_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.Text) # Stored as JSON
    weekly_hours = db.Column(db.Integer)
    work_mode = db.Column(db.String(20))
    location = db.Column(db.String(100))
    qualifications = db.Column(db.Text) # Stored as JSON
    accommodations = db.Column(db.Text) # Stored as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields
    application_period_start = db.Column(db.DateTime)
    application_period_end = db.Column(db.DateTime)
    application_status = db.Column(db.String(50), default='Open')
    job_type = db.Column(db.String(50))
    application_materials = db.Column(db.Text) # Stored as JSON
    job_description = db.Column(db.Text)
    application_link = db.Column(db.String(200))

    def get_industry_list(self):
        return json.loads(self.industry) if self.industry else []

    def set_industry_list(self, industry_list):
        self.industry = json.dumps(industry_list)

    def get_qualifications_list(self):
        return json.loads(self.qualifications) if self.qualifications else []

    def set_qualifications_list(self, qualifications_list):
        self.qualifications = json.dumps(qualifications_list)

    def get_accommodations_list(self):
        return json.loads(self.accommodations) if self.accommodations else []

    def set_accommodations_list(self, accommodations_list):
        self.accommodations = json.dumps(accommodations_list)
        
    def get_application_materials_list(self):
        return json.loads(self.application_materials) if self.application_materials else []
        
    def set_application_materials_list(self, materials_list):
        self.application_materials = json.dumps(materials_list)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'role_name': self.role_name,
            'industry': self.get_industry_list(),
            'weekly_hours': self.weekly_hours,
            'work_mode': self.work_mode,
            'location': self.location,
            'qualifications': self.get_qualifications_list(),
            'accommodations': self.get_accommodations_list(),
            'application_period_start': self.application_period_start,
            'application_period_end': self.application_period_end,
            'application_status': self.application_status,
            'job_type': self.job_type,
            'application_materials': self.get_application_materials_list(),
            'job_description': self.job_description,
            'application_link': self.application_link
        }
