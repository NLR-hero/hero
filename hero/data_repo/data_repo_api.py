import requests
import os
import json
import base64
import logging

from ..resilient_session import ResilientSession

log = logging.getLogger("hero:auth:cognito")

# HERO_BASE_URL = "https://dev-hero.stratus.nrel.gov/repo/api/v1"
# HERO_BASE_URL = "http://localhost:8002/data-repo/api/v1"

HERO_DATA_REPO_API_URL = os.environ.get(
    "HERO_DATA_REPO_API_URL",
    "https://db1kvdyyqlha5.cloudfront.net/data-repo/api/v1",  # TODO... fix this for the datarepo
)


def create_project(token, datahubId, project):
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/project"

    payload = json.dumps(project)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def create_dataset(token, datahubId, data):
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/dataset"

    payload = json.dumps(data)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def create_file(token, datahubId, fileData):
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/file"

    payload = json.dumps(fileData)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def get_or_create_file(token, datahubId, fileData):

    # if filename exists, return it
    try:
        filename = read_file_by_name(token, datahubId, "File", fileData["name"])
        return filename

    except Exception as e:
        # create file
        filename = create_file(token, datahubId, fileData)
        return filename


def upload_file(token, datahubId, fileItem, file_path):
    url = f'{HERO_DATA_REPO_API_URL}/{datahubId}/files/upload/{fileItem["id"]}'
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    signed_url = response.json()["url"]

    # file_path = f'./tmp/{fileItem["name"]}'  # The local file you want to upload

    # Read the file data
    with open(file_path, "rb") as file:
        file_data = file.read()

    # Make a PUT request to the signed URL
    response = s.put(signed_url, data=file_data)

    # Check if the upload was successful (HTTP status code 200)
    if response.status_code == 200:
        print("File upload successful!")
    else:
        print(
            f"File upload failed with status code {response.status_code}: {response.text}"
        )


def download_file(token, datahubId, fileItem, file_path):
    print("START DOWNLOAD")
    url = f'{HERO_DATA_REPO_API_URL}/{datahubId}/files/download/{fileItem["id"]}'
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)

    signed_url = response.json()["url"]

    with s.get(signed_url, stream=True) as r:
        r.raise_for_status()
        try:
            with open(f"{file_path}", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            print(f"File write to disk failed with error: {str(e)}")

    if response.status_code == 200:
        print("File download successful!")
    else:
        print(
            f"File download failed with status code {response.status_code}: {response.text}"
        )


def read_project_by_name(token, datahubId, metatype, name):
    url = (
        f"{HERO_DATA_REPO_API_URL}/{datahubId}/project/metatype/{metatype}?name={name}"
    )
    print(url)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)

    response.raise_for_status()
    return response.json()


def read_dataset_by_name(token, datahubId, metatype, name):
    url = (
        f"{HERO_DATA_REPO_API_URL}/{datahubId}/dataset/metatype/{metatype}?name={name}"
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)

    response.raise_for_status()
    return response.json()


def read_file_by_name(token, datahubId, metatype, name):
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/file/metatype/{metatype}?name={name}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = Request()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()


def read_projects_by_datarepo(token, datahubId):
    print("calling...")
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/projects"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()


def read_datasets_by_project(token, datahubId, project_id):
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/project/{project_id}/datasets"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()


def read_files_by_dataset(token, datahubId, dataset_id):
    url = f"{HERO_DATA_REPO_API_URL}/{datahubId}/dataset/{dataset_id}/files"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()
