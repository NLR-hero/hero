import requests
import os
import json
import base64
import logging

log = logging.getLogger('hero:auth:cognito')

HERO_BASE_URL = 'https://dev-hero.stratus.nrel.gov/repo/api/v2'

def create_project(token, project):
    '''
    {
        "name": "Raw Data",
        "metadata": {},
        "datahubId": "6fd4cda0-37b1-4767-9188-3383dc90a5a6"
    }
    '''
    url = f'{HERO_BASE_URL}/project'

    payload = json.dumps(project)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request('POST', url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

def create_dataset(token, dataset):
    '''
    {
        "name": "Raw Data",
        "metadata": {},
        "projectId": "6fd4cda0-37b1-4767-9188-3383dc90a5a6"
    }
    '''
    url = f'{HERO_BASE_URL}/dataset'

    payload = json.dumps(dataset)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request('POST', url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

def create_file(token, file):
    '''
    {
        "name": filename,
        "metadata": {},
        "datasetId": "6a232b47-f52e-444d-b815-dd7d13b73d7b"
    }
    '''
    url = f'{HERO_BASE_URL}/file'

    payload = json.dumps(file)
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

def upload_file(token, file, file_path):
    '''
    fileItem = create_file(filename)
    print('FileItem', fileItem)
    file_path = f'/tmp/{file["name"]}'
    '''

    url = f'{HERO_BASE_URL}/files/put-object-url/{file["id"]}'

    payload = json.dumps({
        "bucket": "dev-aws-repo-files",
        "key": f'{file["id"]}/{file["name"]}'
    })
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    signed_url = response.json()['url']

    # Read the file data
    with open(file_path, "rb") as file:
        file_data = file.read()

    # Make a PUT request to the signed URL
    response = requests.put(signed_url, data=file_data)

    # Check if the upload was successful (HTTP status code 200)
    if response.status_code == 200:
        print("File upload successful!")
    else:
        print(f"File upload failed with status code {response.status_code}: {response.text}")

