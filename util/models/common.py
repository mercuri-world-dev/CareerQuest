from enum import Enum

class Site(Enum):
  LINKEDIN = "linkedin"
  INDEED = "indeed"
  ZIP_RECRUITER = "zip_recruiter"
  GLASSDOOR = "glassdoor"
  GOOGLE = "google"
  BAYT = "bayt"
  NAUKRI = "naukri"
  MERCURI = "mercuri"

  @classmethod
  def to_shorthand(cls, site: 'Site') -> str:
    match site:
      case cls.LINKEDIN: 
        return "li"
      case cls.INDEED:
        return "in"
      case cls.ZIP_RECRUITER:
        return "zr"
      case cls.GLASSDOOR:
        return "gd"
      case cls.GOOGLE:
        return "go"
      case cls.BAYT:
        return "bayt"
      case cls.NAUKRI:
        return "nk"
      case cls.MERCURI:
        return "me"
      case _:
        raise ValueError(f"Unknown site: {site}")  

class JobType(Enum):
  FULLTIME = "fulltime"
  PARTTIME = "parttime"
  INTERNSHIP = "internship"
  CONTRACT = "contract"
  
  @classmethod
  def from_string(cls, job_type: str):
    return cls[job_type.upper()] if job_type.upper() in cls.__members__ else None