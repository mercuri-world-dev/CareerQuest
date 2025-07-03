from requests import Response

from util.classes.result import Result
from util.models import LinkedinJob, Site

def parse_jobs_response(provider: Site, data: list[dict]) -> Result[list[LinkedinJob] | None]:
  match provider:
    case Site.LINKEDIN:
      jobs = []
      for job in data:
        job_obj = LinkedinJob.from_response(job)
        jobs.append(job_obj)
    case _:
      return Result(success=False, data=None, error=f"Unsupported provider: {provider}")
  return Result(data=jobs, success=True)

def parse_job_response(provider: Site, response: Response) -> Result[LinkedinJob | None]:
  data = response.json()
  match provider:
    case Site.LINKEDIN:
      job = LinkedinJob.from_response(data)
    case _:
      return Result(success=False, data=None, error=f"Unsupported provider: {provider}")
  return Result(data=job, success=True)

# JobPost
# ├── title
# ├── company
# ├── company_url
# ├── job_url
# ├── location
# │   ├── country
# │   ├── city
# │   ├── state
# ├── is_remote
# ├── description
# ├── job_type: fulltime, parttime, internship, contract
# ├── job_function
# │   ├── interval: yearly, monthly, weekly, daily, hourly
# │   ├── min_amount
# │   ├── max_amount
# │   ├── currency
# │   └── salary_source: direct_data, description (parsed from posting)
# ├── date_posted
# └── emails

# Linkedin specific
# └── job_level

# Linkedin & Indeed specific
# └── company_industry

# Indeed specific
# ├── company_country
# ├── company_addresses
# ├── company_employees_label
# ├── company_revenue_label
# ├── company_description
# └── company_logo

# Naukri specific
# ├── skills
# ├── experience_range
# ├── company_rating
# ├── company_reviews_count
# ├── vacancy_count
# └── work_from_home_type