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

@dataclass
class CompanyProfile:
  id: str
  company_name: str
  industry: Optional[str] = None
  description: Optional[str] = None
  website: Optional[str] = None
  location: Optional[str] = None