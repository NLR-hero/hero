import os
import requests
import base64

from . job import Job


class Gantry():

    def __init__(self):
        # 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev'
        self.base_api_url = os.environ['GANTRY_BASE_API_URL']
        # 'https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token'
        self.auth_url = os.environ['GANTRY_AUTH_URL']
        self.resource_name = os.environ['GANTRY_RESOURCE_NAME']
        self._get_token()
        self.headers = {
            'Authorization': self.bearer_token
        }
        # self._get_job()

    def _get_token(self):
        # TODO: set as a Kubernetes secret and pull in from environment variable
        # b'66eu4vteg7q6hbooktmi717hgb:1tq6f4ac8bbfk4cka2oj7n6643cgiledmjjoak7rul8j9bgo0hoo'
        app_client_id_secret = os.environ['GANTRY_APP_CLIENT'].encode('utf-8')
        scopes = 'dev-model-api/ops'

        # Request access_token following client credentials grant flow
        basic_auth = f'Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}'
        response = requests.post(self.auth_url,
                                 data=f'grant_type=client_credentials&scope={scopes}',
                                 headers={
                                     'Authorization': basic_auth,
                                     'Content-Type': 'application/x-www-form-urlencoded'
                                 }, verify=False)
        # print(response.json())
        self.access_token = response.json()['access_token']
        self.bearer_token = f'Bearer {self.access_token}'

    def get_job_data(self):
        self.job = requests.post(self.base_api_url + '/api/job/' +
                                 os.environ['GANTRY_JOB_ID'] + '/run', headers=self.headers).json()
        if not self.job['success']:
            print('Job does not exist')
            exit()
        if 'job_description' not in self.job['data']:
            print('Job description not defined')
            exit()

        self.data = self.job['data']['job_description']

    def add_result(self, result, job_id=None):
        if job_id is None:
            requests.post(self.base_api_url + '/api/job/' +
                          str(self.job['data']['id']) + '/result', json=result, headers=self.headers)
        else:
            requests.post(self.base_api_url + '/api/job/' +
                          str(job_id) + '/result', json=result, headers=self.headers)

    def get_job(self):
        if 'GANTRY_JOB_ID' in os.environ.keys():
            self.job = requests.post(self.base_api_url + '/api/job/' +
                                     os.environ['GANTRY_JOB_ID'] + '/run', headers=self.headers).json()
            if not self.job['success']:
                print('Job does not exist')
                exit()
            if 'job_description' not in self.job['data']:
                print('Job description not defined')
                exit()

            self.data = self.job['data']['job_description']
            return Job(self.job['data'])
        else:
            # TODO call API
            return "example"

    def get_next_job(self):
        for job in [x for x in self.jobs() if job.status != "complete"]:
            if job._packet['status'] not in ['done', 'running']:
                return job
        return None

    def jobs(self):
        jobs = requests.get(self.base_api_url +
                            '/api/jobs/', headers=self.headers)

        results = []
        for job in jobs.json()['data']:
            if (job['resource_name'] == self.resource_name):
                results.append(Job(job))
        return results

    def submit_job(self, job):

        job_template = {
            "queue_name": "standard",
            "status": "ready",
            "priority": None,
            "resource_name": self.resource_name,
            "job_description": job
        }
        res = requests.post(self.base_api_url + '/api/jobs/',
                            json=job_template,
                            headers=self.headers)
        return res
