from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from gotrue import datetime

from .common import Site, JobType

class ApplicationStatus(Enum):
  OPEN = True
  CLOSED = False

class Interval(Enum):
  YEARLY = "yearly"
  MONTHLY = "monthly"
  WEEKLY = "weekly"
  DAILY = "daily"
  HOURLY = "hourly"

  @classmethod
  def from_string(cls, interval: str):
    return cls[interval.upper()] if interval.upper() in cls.__members__ else None

class SalarySource(Enum):
  DIRECT_DATA = "direct_data"
  DESCRIPTION = "description"

  @classmethod
  def from_string(cls, source: str):
    return cls[source.upper()] if source.upper() in cls.__members__ else None

@dataclass 
class JobFunction:
  interval: Optional[Interval] = None
  min_amount: Optional[float] = None
  max_amount: Optional[float] = None
  currency: Optional[str] = None
  salary_source: Optional[SalarySource] = None
  
  def to_dict(self):
    return {k: v for k, v in self.__dict__.items() if v is not None}
  
  @classmethod
  def from_dict(cls, data: dict):
    interval = data.get('interval')
    salary_source = data.get('salary_source')
    return cls(
      interval=Interval.from_string(interval) if interval else None,
      min_amount=data.get('min_amount'),
      max_amount=data.get('max_amount'),
      currency=data.get('currency'),
      salary_source=SalarySource.from_string(salary_source) if salary_source else None
    )

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
class SupabaseJobProps:
  id: int
  company_profile_id: int

@dataclass
class JobSiteSpecific(ABC):

  @classmethod
  @abstractmethod
  def from_response(cls, data: dict) -> 'JobSiteSpecific':
    pass

  @abstractmethod
  def to_supabase_dict(self) -> dict:
    pass
  
  def to_dict(self) -> dict:
    return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class Job(ABC):
  id: str
  provider: Site
  company_name: str
  role_name: str 
  company_id: Optional[str] = None  
  supabase_props: Optional[SupabaseJobProps] = None
  industry: Optional[str] = None
  job_url: Optional[str] = None 
  location: Optional[str] = None
  is_remote: Optional[bool] = None
  description: Optional[str] = None
  job_type: Optional[JobType] = None
  job_function: Optional[JobFunction] = None
  date_posted: Optional[datetime] = None
  emails: Optional[list[str]] = None
  site_specific_fields: Optional[JobSiteSpecific] = None

  @property
  def provider_disp(self) -> str:
    return (self.provider.value if isinstance(self.provider, Site) else self.provider).capitalize()
  
  @property
  def date_posted_disp(self) -> str:
    if not self.date_posted:
      return "Not provided"
    return self.date_posted.strftime("%Y-%m-%d")
  
  def to_supabase_dict(self) -> dict:
    try:
      data = {
        'id': self.id,
        'provider': self.provider.value,
        'company_name': self.company_name,
        'role_name': self.role_name,
        'company_id': self.company_id,
        'industry': self.industry,
        'job_url': self.job_url,
        'location': self.location,
        'is_remote': self.is_remote,
        'description': self.description,
        'job_type': self.job_type.value if self.job_type else None,
        'job_function': self.job_function.to_dict() if self.job_function else None,
        'date_posted': int(self.date_posted.timestamp() * 1000) if self.date_posted else None,
        'emails': ', '.join(self.emails) if self.emails else None,
        **(self.site_specific_fields.to_supabase_dict() if self.site_specific_fields else {})
      }
      return data
    except Exception as e:
      raise ValueError(f"Failed to convert job to Supabase dict: {str(e)}")

  @classmethod
  def from_response(cls, data: dict):
    if 'id' not in data or not data['id']:
      raise ValueError("Job data must contain an 'id' field")
    provider: Site = Site[data.get('site', 'mercuri').upper()]
    if 'company' not in data or not data['company']:
      raise ValueError("Job data must contain a 'company' field")
    if 'title' not in data or not data['title']:
      raise ValueError("Job data must contain a 'title' field")
    job_type = data['job_type']
    job_function = data['job_function']
    if isinstance(data.get('emails'), str):
      emails = [email.strip() for email in data['emails'].split(',')]
    else:
      emails = data.get('emails', [])
    match provider:
      case Site.LINKEDIN:
        site_specific_fields = JobLinkedInSpecific.from_response(data)
      case Site.NAUKRI:
        site_specific_fields = JobNaukriSpecific.from_response(data)
      case Site.MERCURI:
        site_specific_fields = JobMercuriSpecific.from_response(data)
      case _:
        site_specific_fields = None    
    return cls(
      id=data['id'],
      provider=provider,
      company_name=data['company'],
      role_name=data['title'],
      industry=data.get('industry'),
      job_url=data.get('job_url_direct', data.get('job_url', '')),
      location=data.get('location', ''),
      is_remote=data.get('is_remote', False),
      description=data.get('description', ''),
      job_type=JobType.from_string(job_type) if job_type else None,
      job_function=JobFunction.from_dict(job_function) if job_function else None,
      date_posted=datetime.fromtimestamp(data['date_posted']/1000) if data.get('date_posted') else None,
      emails=emails,
      site_specific_fields=site_specific_fields,
    )
  
@dataclass
class JobWithCompatibility(Job):
  compatibility_score: Optional[float] = None

@dataclass
class JobWithCompatibilityFactors(JobWithCompatibility):
  factors: Optional[JobFactors] = None

@dataclass
class JobLinkedInSpecific(JobSiteSpecific):
  job_level: Optional[str] = None
  company_industry: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'JobLinkedInSpecific':
    job_level = data.get('job_level')
    return cls(
      job_level=job_level if job_level != '' else None,
      company_industry=data.get('company_industry'),
    )
  
  def to_supabase_dict(self) -> dict:
    data = {
      'job_level': self.job_level,
      'company_industry': self.company_industry
    }
    return data

@dataclass
class JobNaukriSpecific(JobSiteSpecific):
  skills: Optional[str] = None
  experience_range: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'JobNaukriSpecific':
    return cls(
      skills=data.get('skills'),
      experience_range=data.get('experience_range')
    )

  def to_supabase_dict(self) -> dict:
    data = {
      'skills': self.skills,
      'experience_range': self.experience_range
    }
    return data
  
@dataclass
class JobMercuriSpecific(JobSiteSpecific):
  additional_fields: Optional[dict] = None

  @classmethod
  def from_response(cls, data: dict) -> 'JobMercuriSpecific':
    return cls(
      additional_fields=data.get('additional_fields', {})
    )
  
  def to_supabase_dict(self) -> dict:
    data = {
      'additional_fields': self.additional_fields
    }
    return data