from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .common import JobType, Site

@dataclass 
class CompanySiteSpecific(ABC):

  @classmethod
  @abstractmethod
  def from_response(cls, data: dict) -> 'CompanySiteSpecific':
    pass

  def to_dict(self) -> dict:
    return {k: v for k, v in self.__dict__.items() if v is not None}
  
@dataclass
class CompanyLinkedInSpecific(CompanySiteSpecific): 
  industry: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'CompanyLinkedInSpecific':
    return cls(
      industry=data.get('company_industry')
    )

@dataclass
class CompanyIndeedSpecific(CompanySiteSpecific):
  industry: Optional[str] = None
  country: Optional[str] = None
  addresses: Optional[list[str]] = None
  employees_label: Optional[str] = None
  revenue_label: Optional[str] = None
  provided_description: Optional[str] = None
  logo_url: Optional[str] = None

  @classmethod
  def from_response(cls, data: dict) -> 'CompanyIndeedSpecific':
    return cls(
      industry=data.get('company_industry'),
      country=data.get('company_country'),
      addresses=data.get('company_addresses', []),
      employees_label=data.get('company_employees_label'),
      revenue_label=data.get('company_revenue_label'),
      provided_description=data.get('company_description'),
      logo_url=data.get('company_logo')
    )

@dataclass
class CompanyNaukriSpecific(CompanySiteSpecific):
  rating: Optional[float] = None
  reviews_count: Optional[int] = None
  vacancy_count: Optional[int] = None

  @classmethod
  def from_response(cls, data: dict) -> 'CompanyNaukriSpecific':
    return cls(
      rating=data.get('company_rating'),
      reviews_count=data.get('company_reviews_count'),
      vacancy_count=data.get('company_vacancy_count')
    )
  
class CompanyMercuriSpecific(CompanySiteSpecific):
  additional_fields: Optional[dict] = None

@dataclass
class CompanyProfile:
  company_gen_id: str
  provider: Site
  company_name: str
  mercuri_company_id: Optional[int] = None
  company_url: Optional[str] = None
  locations: Optional[list[str]] = None
  job_industries: Optional[list[str]] = None
  has_offered_remote: Optional[bool] = None 
  past_job_types_offered: Optional[list[JobType]] = None
  site_specific_fields: Optional[CompanySiteSpecific] = None

  @classmethod
  def get_unique_id(cls, name, provider) -> str:
    return f"{Site.to_shorthand(provider)}-{name.lower()}"

  @classmethod
  def from_response(cls, data: dict):
    if 'company' not in data:
      raise ValueError("Missing 'company' field in data")
    name: str = data['company']
    provider: Site = Site[data.get('site', 'mercuri').upper()]
    match provider:
      case Site.LINKEDIN:
        site_specific_fields = CompanyLinkedInSpecific.from_response(data)
      case Site.INDEED:
        site_specific_fields = CompanyIndeedSpecific.from_response(data)
      case Site.NAUKRI:
        site_specific_fields = CompanyNaukriSpecific.from_response(data)
      case _:
        site_specific_fields = None
    return cls(
      company_gen_id=CompanyProfile.get_unique_id(name, provider),
      provider=Site[data.get('site', 'mercuri').upper()],
      company_name=data['company'],
      company_url=data.get('company_url'),
      site_specific_fields=site_specific_fields, 
    )
  
@dataclass
class MercuriCompanyInfo:
  id: int
  company_name: str
  description: Optional[str] = None
  past_accomodations: Optional[list[str]] = None