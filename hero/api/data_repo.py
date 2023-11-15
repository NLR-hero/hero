import requests
import os
import json
import base64
import logging

log = logging.getLogger('hero:auth:cognito')

HERO_BASE_URL = 'https://dev-hero.stratus.nrel.gov/repo/api/v3'

def create_project(token, datahubId, project):
    url = f'{HERO_BASE_URL}/{datahubId}/project'

    payload = json.dumps(project)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request('POST', url, headers=headers, data=payload)

    response.raise_for_status()

    return response.json()

def create_dataset(token, datahubId, data):
    url = f'{HERO_BASE_URL}/{datahubId}/dataset'

    payload = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response.raise_for_status()
    print(response.content)
    return response.json()

def create_file(token, datahubId, fileData):
    url = f'{HERO_BASE_URL}/{datahubId}/file'

    payload = json.dumps(fileData)
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()

    return response.json()

def upload_file(token, datahubId, fileItem, file_path):
    url = f'{HERO_BASE_URL}/{datahubId}/files/upload/{fileItem["id"]}'
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    response = requests.request("GET", url, headers=headers)

    signed_url = response.json()['url']

    # file_path = f'./tmp/{fileItem["name"]}'  # The local file you want to upload

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


def read_project_by_name(token, datahubId, metatype, name):
    url = f'{HERO_BASE_URL}/{datahubId}/project/metatype/{metatype}?name={name}'
    print(url)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request('GET', url, headers=headers)

    response.raise_for_status()

    return response.json()

def read_dataset_by_name(token, datahubId, metatype, name):
    url = f'{HERO_BASE_URL}/{datahubId}/dataset/metatype/{metatype}?name={name}'
    print(url)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request('GET', url, headers=headers)

    response.raise_for_status()

    return response.json()

def read_file_by_name(token, datahubId, metatype, name):
    url = f'{HERO_BASE_URL}/{datahubId}/file/metatype/{metatype}?name={name}'
    print(url)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request('GET', url, headers=headers)

    response.raise_for_status()

    return response.json()