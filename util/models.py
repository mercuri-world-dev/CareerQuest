from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from gotrue import datetime

class ApplicationStatus(Enum):
  OPEN = True
  CLOSED = False

class Site(Enum):
  LINKEDIN = "linkedin"
  INDEED = "indeed"
  ZIP_RECRUITER = "zip_recruiter"
  GLASSDOOR = "glassdoor"
  GOOGLE = "google"
  BAYT = "bayt"
  NAUKRI = "naukri"
  MERCURI = "mercuri"

class JobType(Enum):
  FULLTIME = "fulltime"
  PARTTIME = "parttime"
  INTERNSHIP = "internship"
  CONTRACT = "contract"
  
  @classmethod
  def from_string(cls, job_type: str):
    return cls[job_type.upper()] if job_type.upper() in cls.__members__ else None

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

# @dataclass
# class Location:
#   country: Optional[str] = None
#   city: Optional[str] = None
#   state: Optional[str] = None

#   def to_dict(self):
#     return {k: v for k, v in self.__dict__.items() if v is not None}
  
#   @classmethod
#   def from_dict(cls, data: dict):
#     return cls(
#       country=data.get('country'),
#       city=data.get('city'),
#       state=data.get('state')
#     )

@dataclass
class SupabaseJobProps:
  id: int
  company_profile_id: int
  user_profile_id: int

@dataclass
class SiteSpecificFields(ABC):

  @classmethod
  @abstractmethod
  def from_response(cls, data: dict) -> 'SiteSpecificFields':
    pass

@dataclass
class NewJob(ABC):
  provider: Site
  company_name: str
  role_name: str
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
  site_specific_fields: Optional[SiteSpecificFields] = None

  @classmethod
  def from_response(cls, data: dict):
    job_type = data.get('job_type')
    job_function = data.get('job_function')
    provider: Site = data.get('provider', 'MERCURI').upper()
    match provider:
      case Site.LINKEDIN:
        site_specific_fields = LinkedInSpecific.from_response(data)
      case Site.INDEED:
        site_specific_fields = IndeedSpecific.from_response(data)
      case Site.NAUKRI:
        site_specific_fields = NaukriSpecific.from_response(data)
      case Site.MERCURI:
        site_specific_fields = MercuriSpecific.from_response(data)
      case _:
        site_specific_fields = None
    return cls(
      provider=provider,
      company_name=data.get('company', ''),
      role_name=data.get('title', ''),
      industry=data.get('industry'),
      job_url=data.get('job_url'),
      location=data.get('location', ''),
      is_remote=data.get('is_remote', False),
      description=data.get('description', ''),
      job_type=JobType.from_string(job_type) if job_type else None,
      job_function=JobFunction.from_dict(job_function) if job_function else None,
      date_posted=data.get('date_posted'),
      emails=data.get('emails', []),
      site_specific_fields=site_specific_fields,
    )
  
@dataclass
class NewJobWithCompatibility(NewJob):
  compatibility_score: Optional[float] = None

@dataclass
class NewJobWithCompatibilityFactors(NewJobWithCompatibility):
  factors: Optional[JobFactors] = None
 
@dataclass
class LinkedInSpecific(SiteSpecificFields):
  job_level: Optional[str] = None
  company_industry: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'LinkedInSpecific':
    return cls(
      job_level=data.get('job_level'),
      company_industry=data.get('company_industry'),
    )
  
@dataclass
class IndeedSpecific(SiteSpecificFields):
  company_country: Optional[str] = None
  company_addresses: Optional[list[str]] = None
  company_employees_label: Optional[str] = None
  company_revenue_label: Optional[str] = None
  company_description: Optional[str] = None
  company_logo: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'IndeedSpecific':
    return cls(
      company_country=data.get('company_country'),
      company_addresses=data.get('company_addresses', []),
      company_employees_label=data.get('company_employees_label'),
      company_revenue_label=data.get('company_revenue_label'),
      company_description=data.get('company_description'),
      company_logo=data.get('company_logo')
    )

@dataclass
class NaukriSpecific(SiteSpecificFields):
  skills: Optional[str] = None
  experience_range: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'NaukriSpecific':
    return cls(
      skills=data.get('skills'),
      experience_range=data.get('experience_range')
    )
  
@dataclass
class MercuriSpecific(SiteSpecificFields):
  additional_fields: Optional[dict] = None

  @classmethod
  def from_response(cls, data: dict) -> 'MercuriSpecific':
    return cls(
      additional_fields=data.get('additional_fields', {})
    )

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
  provider: Optional[Site] = None

  @classmethod    
  def from_supabase_dict(cls, data: dict):
    return cls(
      id=int(data.get('id', 0)),
      company_profile_id=int(data.get('company_profile_id', 0)),
      company_name=data.get('company_name', ''),
      role_name=data.get('role_name', ''),
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
      id=int(data.get('id', 0)),
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
      id=data.get('id', ''),
      company_name=data.get('company_name', ''),
      industry=data.get('industry'),
      description=data.get('description'),
      website=data.get('website'),
      location=data.get('location')
    )