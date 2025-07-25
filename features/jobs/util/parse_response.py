from requests import Response

from util.classes.result import Result
from util.models.common import Site
from util.models.job_model import Job

def parse_jobs_response(provider: Site, data: list[dict]) -> Result[list[Job] | None]:
  try:
    jobs = [Job.from_response(job_datum) for job_datum in data]
  except Exception as e:
    return Result(success=False, data=None, error=f"Failed to parse jobs: {str(e)}")
  return Result(data=jobs, success=True)

def parse_job_response(provider: Site, response: Response) -> Result[Job | None]:
  data = response.json()
  try:
    job = Job.from_response(data)
  except Exception as e:
    return Result(success=False, data=None, error=f"Failed to parse job: {str(e)}")
  return Result(data=job, success=True)