import io
import os
import mimetypes

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = service_account.Credentials.from_service_account_file(
        key_file_location)

    scoped_credentials = credentials.with_scopes(scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=scoped_credentials)

    return service


def find_files_in_folder(parent_folder, service):
    """Find the files in a given parent folder

    Args:
        parent_folder: Folder to find the children for
        service: Google Drive service object

    Returns:
        A lists of file objects containing id and name
    """
    parent_id = find_folder(parent_folder, service)

    if not parent_id:
        return

    children_files = []
    page_token = None
    while True:
        results = service.files().list(
            q=f'"{parent_id}" in parents',
            pageSize=10,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token).execute()
        items = results.get('files', [])
        children_files.extend(items)

        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

    return children_files


def download_file(file_id, folder, file_name, service):
    """Download a file by id

    Args:
        file_id: id of the file ot be downloaded
        folder: Local folder to download the file to
        file_name: name of the file to be created
        service: Google Drive service object
    """
    file_path = os.path.join(folder, file_name)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'w')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))


def upload_file(folder, file_name, service, parent_folder_id=None):
    """Uploads a file

    Args:
        folder: Local folder where the file is located
        file_name: name of the file to be updated
        service: Google Drive service object
        parent_folder_id: Optional parent folder id in Google Drive
    """
    file_path = os.path.join(folder, file_name)
    mime_type = mimetypes.guess_type(file_path)

    file_metadata = {'name': file_name}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    media = MediaFileUpload(file_path, mimetype=mime_type[0])
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
    print('File ID: %s' % file.get('id'))


def create_folder(folder_name, service, parent_folder_id=None):
    """Create a folder in Google Drive

    Args:
        folder_name: Name of the new folder
        service: Google Drive service object
        parent_folder_id: Optional parent folder id in Google Drive
    """
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    file = service.files().create(body=file_metadata,
                                  fields='id').execute()
    print('Folder ID: %s' % file.get('id'))


def delete_file(file_name, service):
    """Deletes a file permanently

    Args:
        file_name: File name to be deleted
        service: Google Drive service object
    """
    file_id = find_file(file_name, service)
    if file_id:
        service.files().delete(fileId=file_id).execute()
        print('File deleted')


def copy_file(file_name, service, parent_folder_id=None, new_name=None):
    """Copy a file

    Args:
        file_name: Name of the file ot be copied
        service: Google Drive service object
        parent_folder_id: Optional parent folder to create the copy in
        new_name: Optional new file name
    """
    file_id = find_file(file_name, service)
    if file_id:
        file_metadata = {}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        if new_name:
            file_metadata['name'] = new_name
        file = service.files().copy(fileId=file_id,
                                    body=file_metadata,
                                    fields='id').execute()
        print('Folder ID: %s' % file.get('id'))


def find_file(file_name, service):
    """Find a file by name

    Args:
        file_name: Name of the file to search
        service: Google Drive service object

    Returns:
        File ID
    """
    results = service.files().list(q=f"name = '{file_name}'",
                                   pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print(f'File {file_name} was not found.')
        return
    return items[0]['id']


def find_folder(folder, service):
    """Find a folder by name

    Args:
        folder: Name of the folder
        service: Google Drive service object

    Returns:
        File ID
    """
    results = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name = '{folder}'",
                                   pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print(f'Folder {folder} was not found.')
        return
    return items[0]['id']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/drive'
    key_file_location = 'key.json'

    try:
        # Authenticate and construct service.
        service = get_service(
            api_name='drive',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

        print('Operations')
        print('1. Find files in folder')
        print('2. Download file')
        print('3. Upload file')
        print('4. Create folder')
        print('5. Delete file')
        print('6. Copy file')
        option = int(input('Select an option: '))

        if option == 1:
            folder = input('Enter folder name: ')
            files = find_files_in_folder(folder, service)
            if files:
                print('Files:')
                for file in files:
                    print(u'{0} ({1})'.format(file['name'], file['id']))
            else:
                print(f'No files found in folder {folder}')

        if option == 2:
            file_name = input('Enter file name to download: ')
            folder = input('Enter folder where the file will be saved: ')

            file_id = find_file(file_name, service)
            if file_id:
                download_file(file_id, folder, file_name, service)

        if option == 3:
            folder = input('Enter folder where the file is located: ')
            file_name = input('Enter file name to be uploaded: ')
            parent_folder = input('Enter parent folder in drive (enter to upload to root): ')
            if parent_folder:
                parent_folder_id = find_folder(parent_folder, service)
                if parent_folder_id:
                    upload_file(folder, file_name, service, parent_folder_id)
            else:
                upload_file(folder, file_name, service)

        if option == 4:
            folder = input('Enter folder name to be created: ')
            parent_folder = input('Enter parent folder in drive (enter to upload to root): ')
            if parent_folder:
                parent_folder_id = find_folder(parent_folder, service)
                if parent_folder_id:
                    create_folder(folder, service, parent_folder_id)
            else:
                create_folder(folder, service)

        if option == 5:
            file_name = input('Enter file name to be deleted (permanently): ')
            delete_file(file_name, service)

        if option == 6:
            file_name = input('Enter file name to be copied: ')
            parent_folder = input('Enter parent folder for new file (enter to same folder): ')
            new_name = input('Enter new file name (enter to keep same name): ')
            if parent_folder:
                parent_folder_id = find_folder(parent_folder, service)
                if parent_folder_id:
                    copy_file(file_name, service, parent_folder_id, new_name)
            else:
                copy_file(file_name, service, new_name=new_name)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
