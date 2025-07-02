from dataclasses import dataclass
from enum import Enum
from typing import Optional

from gotrue import datetime

class ApplicationStatus(Enum):
  OPEN = True
  CLOSED = False

@dataclass
class JobFactors:
  location_score: Optional[float] = None
  hours_score: Optional[float] = None
  work_mode_score: Optional[float] = None
  accommodations_score: Optional[float] = None
  qualifications_score: Optional[float] = None
  
  def to_dict(self):
    return {k: v for k, v in self.__dict__.items() if v is not None}
  
  def to_display_dict(self):
    """Converts the factors to a dict with names and percentage scores."""
    return [
      {"name": "Location", "score": round(self.location_score*100) if self.location_score is not None else 0},
      {"name": "Hours", "score": round(self.hours_score*100) if self.hours_score is not None else 0},
      {"name": "Work Mode", "score": round(self.work_mode_score*100) if self.work_mode_score is not None else 0},
      {"name": "Accommodations", "score": round(self.accommodations_score*100) if self.accommodations_score is not None else 0},
      {"name": "Qualifications", "score": round(self.qualifications_score*100) if self.qualifications_score is not None else 0}
    ]

@dataclass
class Job:
  id: int
  company_profile_id: int
  company_name: str
  role_name: int
  industry: Optional[list[str]] = None
  weekly_hours: Optional[int] = None
  work_mode: Optional[str] = None
  location: Optional[str] = None
  qualifications: Optional[list[str]] = None
  accommodations: Optional[list[str]] = None
  application_period_start: Optional[datetime] = None
  application_period_end: Optional[datetime] = None
  application_status: ApplicationStatus = ApplicationStatus.OPEN
  job_type: Optional[str] = None
  application_materials: Optional[list[str]] = None
  job_description: Optional[str] = None
  application_link: Optional[str] = None

  @classmethod    
  def from_supabase_dict(cls, data: dict):
    return cls(
      id=data.get('id'),
      company_profile_id=data.get('company_profile_id'),
      company_name=data.get('company_name'),
      role_name=data.get('role_name'),
      industry=data.get('industry', []),
      weekly_hours=data.get('weekly_hours'),
      work_mode=data.get('work_mode'),
      location=data.get('location'),
      qualifications=data.get('qualifications', []),
      accommodations=data.get('accommodations', []),
      application_period_start=data.get('application_period_start'),
      application_period_end=data.get('application_period_end'),
      application_status=ApplicationStatus(data.get('application_status', True)),
      job_type=data.get('job_type'),
      application_materials=data.get('application_materials', []),
      job_description=data.get('job_description'),
      application_link=data.get('application_link')
    )

@dataclass(kw_only=True)
class JobWithCompatibility(Job):
  compatibility_score: float

@dataclass(kw_only=True)
class JobWithCompatibilityFactors(JobWithCompatibility):
  factors: JobFactors

@dataclass
class UserProfile:
  id: int
  remote_preference: bool
  hybrid_preference: bool
  in_person_preference: bool
  age_range: Optional[str] = None
  hours_per_week: Optional[int] = None
  location: Optional[str] = None
  accommodations: Optional[list[str]] = None
  educational_background: Optional[list[str]] = None

  @classmethod
  def from_supabase_dict(cls, data: dict):
    return cls(
      id=data.get('id'),
      remote_preference=data.get('remote_preference', False),
      hybrid_preference=data.get('hybrid_preference', False),
      in_person_preference=data.get('in_person_preference', False),
      age_range=data.get('age_range'),
      hours_per_week=data.get('hours_per_week'),
      location=data.get('location'),
      accommodations=data.get('accommodations', []),
      educational_background=data.get('educational_background', [])
    )

@dataclass
class CompanyProfile:
  id: str
  company_name: str
  industry: Optional[str] = None
  description: Optional[str] = None
  website: Optional[str] = None
  location: Optional[str] = None

  @classmethod
  def from_supabase_dict(cls, data: dict):
    return cls(
      id=data.get('id'),
      company_name=data.get('company_name'),
      industry=data.get('industry'),
      description=data.get('description'),
      website=data.get('website'),
      location=data.get('location')
    )