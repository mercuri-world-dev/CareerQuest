import json
import os
import requests

from debug.util.mock_data import MOCK_RESPONSE
from util.classes.result import Result
from util.models.common import Site

API_URL = os.environ.get("JOB_SERVICE_URL", "http://localhost:8000")
PROXIES = [
  "188.42.89.150:80",
  "23.227.60.92:80",
  "45.85.119.213:80",
  "localhost:8080"
]

def jobspy_fetch_jobs(
  site_name: str | list[str] | Site | list[Site] | None = None,
  search_term: str | None = None,
  google_search_term: str | None = None,
  location: str | None = None,
  distance: int | None = 50,
  is_remote: bool = False,
  job_type: str | None = None,
  easy_apply: bool | None = None,
  results_wanted: int = 15,
  country_indeed: str = "usa",
  ca_cert: str | None = None,
  description_format: str = "markdown",
  linkedin_fetch_description: bool | None = False,
  linkedin_company_ids: list[int] | None = None,
  offset: int | None = 0,
  hours_old: int | None = None,
  enforce_annual_salary: bool = False,
  verbose: int = 0
) -> Result[list[dict] | None]:
  try:
    # params = {
    #   "site_name": site_name,
    #   "search_term": search_term,
    #   "google_search_term": google_search_term,
    #   "location": location,
    #   "distance": distance,
    #   "is_remote": is_remote,
    #   "job_type": job_type,
    #   "easy_apply": easy_apply,
    #   "results_wanted": results_wanted,
    #   "country_indeed": country_indeed,
    #   "proxies": PROXIES,
    #   "ca_cert": ca_cert,
    #   "description_format": description_format,
    #   "linkedin_fetch_description": linkedin_fetch_description,
    #   "linkedin_company_ids": linkedin_company_ids,
    #   "offset": offset,   
    #   "hours_old": hours_old,
    #   "enforce_annual_salary": enforce_annual_salary,
    #   "verbose": verbose
    # }
    # params = {k: v for k, v in params.items() if v is not None}
    # response = requests.get(f"{API_URL}/jobs/", params=params)
    # if response.status_code != 200:
    #   print(f"Error fetching jobs: {response.status_code} - {response.text}")
    #   return Result(success=False, error=response.text)
    # jobs_data = response.json()
    
    jobs_data = MOCK_RESPONSE
    print(jobs_data)
    
    if not isinstance(jobs_data, list):
      print("Invalid response format: expected a list of jobs")
      return Result(success=False, error="Invalid response format", data=None)
    if not jobs_data:
      print("No jobs found.")
      return Result(success=True, data=[])
    jobs = [job for job in jobs_data if isinstance(job, dict)]
    if not jobs:
      print("No valid jobs found in the response.")
      return Result(success=True, data=[])
    return Result(success=True, data=jobs)
  except Exception as e:
    print(f"Error in jobspy_fetch_jobs: {e}")
    return Result(success=False, error=str(e))