import json
import os

from google.cloud import secretmanager, storage
from google.oauth2 import service_account


def authenticate_with_service_account():
    try:
        if (os.getenv('LOCAL_DEVELOPMENT', 'False') == 'True'):
            credentials_path = os.path.join(
                os.path.abspath(os.curdir), "downloads/creds.json")
            if os.path.exists(credentials_path):
                return service_account.Credentials.from_service_account_file(credentials_path)

        secret_client = secretmanager.SecretManagerServiceClient()
        secret_name = os.getenv('SERVICE_ACCOUNT_SECRET_NAME')
        project_id = os.getenv('PROJECT_ID')

        if not secret_name or not project_id:
            raise EnvironmentError(
                "Required environment variables are not set")

        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = secret_client.access_secret_version(
            request={"name": secret_path})
        credentials_dict = json.loads(response.payload.data.decode("UTF-8"))

        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict)
        print("Successfully authenticated using service account from Secret Manager")
        return credentials

    except Exception as e:
        raise EnvironmentError(f"Failed to load credentials: {str(e)}")


def download_index(bucket_name: str, local_dir: str = "index", credentials=None):
    try:
        client = storage.Client(credentials=credentials)
        bucket = client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()

        downloaded_folders = set()

        os.makedirs(local_dir, exist_ok=True)

        for blob in blobs:
            folder_path = os.path.join(local_dir, os.path.dirname(blob.name))
            os.makedirs(folder_path, exist_ok=True)

            local_file_path = os.path.join(local_dir, blob.name)
            blob.download_to_filename(local_file_path)
            downloaded_folders.add(folder_path)

        print(f"Downloaded folders: {list(downloaded_folders)}")
        return list(downloaded_folders)

    except Exception as e:
        print(f"Error downloading folders: {str(e)}")
        return []


def initialize_data():
    try:
        credentials = authenticate_with_service_account()

        if (os.getenv('LOCAL_DEVELOPMENT', 'False') == 'True'):
            default_local_dir = os.path.join(
                os.path.abspath(os.curdir), "downloads")
        else:
            default_local_dir = os.path.join('/tmp', 'downloads')

        default_bucket_name = os.getenv('BUCKET_NAME', 'covid-tbi')

        print(f"Using storage directory: {default_local_dir}")

        downloaded_folders = download_index(
            bucket_name=default_bucket_name,
            local_dir=default_local_dir,
            credentials=credentials
        )

        if downloaded_folders:
            print("Download completed successfully.")
        else:
            print("No folders were downloaded.")

        return default_local_dir

    except Exception as e:
        print(f"An error occurred during initialization: {str(e)}")
        raise
