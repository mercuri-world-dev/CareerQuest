from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timezone
import uuid
  
@dataclass
class UserProfile:
  id: int
  age_range: Optional[str] = None
  hours_per_week: Optional[int] = None
  location: Optional[str] = None
  accommodations: List[str] = field(default_factory=list)
  educational_background: Optional[str] = None
  remote_preference: bool = False
  hybrid_preference: bool = False
  in_person_preference: bool = False
  created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
  updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

  def __post_init__(self):
    if not self.id:
      self.id = uuid.uuid4().int
  @classmethod
  def from_sb_response(cls, sb_response):
    instance = cls(
      id=sb_response['id'],
      age_range=sb_response.get('age_range'),
      hours_per_week=sb_response.get('hours_per_week'),
      location=sb_response.get('location'),
      educational_background=sb_response.get('educational_background'),
      remote_preference=sb_response.get('remote_preference', False),
      hybrid_preference=sb_response.get('hybrid_preference', False),
      in_person_preference=sb_response.get('in_person_preference', False),
      created_at=datetime.fromisoformat(sb_response['created_at']),
    )
    instance.set_accommodations_list(sb_response.get('accommodations', []))
    instance.set_updated_at()
    return instance

  def get_accommodations_list(self):
    return self.accommodations

  def set_accommodations_list(self, accommodations_list):
    self.accommodations = accommodations_list

  def set_updated_at(self):
    self.updated_at = datetime.now(tz=timezone.utc)

  def to_dict(self):
    return {
      'id': self.id,
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
  created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
  updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

  def __post_init__(self):
    if not self.id:
      self.id = uuid.uuid4().int

  @classmethod
  def from_sb_response(cls, sb_response):
    instance = cls(
      id=sb_response['id'],
      user_id=sb_response['user_id'],
      company_name=sb_response['company_name'],
      description=sb_response.get('description'),
      website=sb_response.get('website'),
      location=sb_response.get('location'),
      created_at=datetime.fromisoformat(sb_response['created_at']),
    )
    instance.set_industry_list(sb_response.get('industry', []))
    instance.set_updated_at()
    return instance
  
  def get_industry_list(self):
    return self.industry

  def set_industry_list(self, industry_list):
    self.industry = industry_list

  def set_updated_at(self):
    self.updated_at = datetime.now(tz=timezone.utc)

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
  application_period_start: Optional[datetime] = None
  application_period_end: Optional[datetime] = None
  application_status: str = "Open"
  job_type: Optional[str] = None
  application_materials: List[str] = field(default_factory=list)
  job_description: Optional[str] = None
  application_link: Optional[str] = None
  created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

  def __post_init__(self):
    if not self.id:
      self.id = str(uuid.uuid4())

  @classmethod
  def from_sb_response(cls, sb_response):
    instance = cls(
      id=sb_response['id'],
      company_profile_id=sb_response['company_profile_id'],
      company_name=sb_response['company_name'],
      role_name=sb_response['role_name'],
      weekly_hours=sb_response.get('weekly_hours'),
      work_mode=sb_response.get('work_mode'),
      location=sb_response.get('location'),
      application_period_start=datetime.fromisoformat(sb_response['application_period_start']) if sb_response.get('application_period_start') else None,
      application_period_end=datetime.fromisoformat(sb_response['application_period_end']) if sb_response.get('application_period_end') else None,
      application_status=sb_response.get('application_status', 'Open'),
      job_type=sb_response.get('job_type'),
      job_description=sb_response.get('job_description'),
      application_link=sb_response.get('application_link'),
      created_at=datetime.fromisoformat(sb_response['created_at'])
    )
    instance.set_industry_list(sb_response.get('industry', []))
    instance.set_qualifications_list(sb_response.get('qualifications', []))
    instance.set_accommodations_list(sb_response.get('accommodations', []))
    instance.set_application_materials_list(sb_response.get('application_materials', []))
    instance.set_updated_at()
    return instance
  
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

  def set_updated_at(self):
    self.updated_at = datetime.now(tz=timezone.utc)

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