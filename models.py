from dataclasses import dataclass, field
import json
from typing import List, Optional
from datetime import datetime
import uuid

@dataclass
class Role:
  id: int
  name: str
  description: Optional[str] = None

@dataclass
class User:
  id: int
  public_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  created_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
  username: str
  email: str
  roles: List[Role] = field(default_factory=list)
  
  def has_role(self, role_name):
    return any(role.name == role_name for role in self.roles)
    
  def to_dict(self):
    return {
      'uid': str(self.id).zfill(10),
      'username': self.username,
      'email': self.email,
    }
  
@dataclass
class UserProfile:
  id: int
  user_public_id: str  # Foreign key to User.public_id
  age_range: Optional[str] = None
  hours_per_week: Optional[int] = None
  location: Optional[str] = None
  accommodations: List[str] = field(default_factory=list)
  educational_background: Optional[str] = None
  remote_preference: bool = False
  hybrid_preference: bool = False
  in_person_preference: bool = False
  company_profile: Optional["CompanyProfile"] = None

  def get_accommodations_list(self):
    return self.accommodations

  def set_accommodations_list(self, accommodations_list):
    self.accommodations = accommodations_list

  def to_dict(self):
    return {
      'uid': str(self.id).zfill(10),
      'age_range': self.age_range,
      'hours_per_week': self.hours_per_week,
      'location': self.location,
      'accommodations': self.get_accommodations_list(),
      'educational_background': self.educational_background,
      'remote_preference': self.remote_preference,
      'hybrid_preference': self.hybrid_preference,
      'in_person_preference': self.in_person_preference
    }

@dataclass
class CompanyProfile:
  id: int
  user_id: int
  company_name: str
  industry: List[str] = field(default_factory=list)
  description: Optional[str] = None
  website: Optional[str] = None
  location: Optional[str] = None
  jobs: List["Job"] = field(default_factory=list)

  def get_industry_list(self):
    return self.industry

  def set_industry_list(self, industry_list):
    self.industry = industry_list

  def to_dict(self):
    return {
      'id': self.id,
      'company_name': self.company_name,
      'industry': self.get_industry_list(),
      'description': self.description,
      'website': self.website,
      'location': self.location
    }

@dataclass
class Job:
  id: str
  company_profile_id: int
  company_name: str
  role_name: str
  industry: List[str] = field(default_factory=list)
  weekly_hours: Optional[int] = None
  work_mode: Optional[str] = None
  location: Optional[str] = None
  qualifications: List[str] = field(default_factory=list)
  accommodations: List[str] = field(default_factory=list)
  created_at: datetime = field(default_factory=datetime.utcnow)
  application_period_start: Optional[datetime] = None
  application_period_end: Optional[datetime] = None
  application_status: str = "Open"
  job_type: Optional[str] = None
  application_materials: List[str] = field(default_factory=list)
  job_description: Optional[str] = None
  application_link: Optional[str] = None

  def get_industry_list(self):
    return self.industry

  def set_industry_list(self, industry_list):
    self.industry = industry_list

  def get_qualifications_list(self):
    return self.qualifications

  def set_qualifications_list(self, qualifications_list):
    self.qualifications = qualifications_list

  def get_accommodations_list(self):
    return self.accommodations

  def set_accommodations_list(self, accommodations_list):
    self.accommodations = accommodations_list

  def get_application_materials_list(self):
    return self.application_materials

  def set_application_materials_list(self, materials_list):
    self.application_materials = materials_list

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
  