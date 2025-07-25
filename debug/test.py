from debug.util.mock_data import MOCK_RESPONSE
from util.models.common import Site
from util.models.company_model import CompanyProfile
from util.models.job_model import Job

job = Job.from_response(MOCK_RESPONSE[1])
print(job)
company = CompanyProfile.from_response(MOCK_RESPONSE[1])
print(company)