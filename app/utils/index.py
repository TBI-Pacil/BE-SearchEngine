import os

from google.cloud import storage
from google.oauth2 import service_account


def authenticate_with_service_account():
    ROOT_DIR = os.path.abspath(os.curdir)
    credentials_path = os.path.join(ROOT_DIR, "downloads/creds.json")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    if not credentials_path or not os.path.exists(credentials_path):
        raise EnvironmentError(
            "The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
        )
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path)
        print(f"Authenticated using service account: {credentials_path}")
        return credentials
    except Exception as e:
        raise EnvironmentError(f"Failed to load credentials: {str(e)}")


def download_index(bucket_name: str, local_dir: str = "index"):
    try:
        client = storage.Client()
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


def main():
    authenticate_with_service_account()

    default_bucket_name = "covid-tbi"
    default_local_dir = os.path.join(os.path.abspath(os.curdir), "downloads")

    try:
        downloaded_folders = download_index(
            bucket_name=default_bucket_name, local_dir=default_local_dir)

        if downloaded_folders:
            print("Download completed successfully.")
            print(f"Downloaded folders: {downloaded_folders}")
        else:
            print("No folders were downloaded.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
