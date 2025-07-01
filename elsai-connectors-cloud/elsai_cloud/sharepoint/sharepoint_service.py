from .implementation import SharePointServiceImplementation
from typing import Dict, List, Any
import os
class SharePointService:

    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None, site_hostname: str = None, site_path: str = None, drive_name: str = None, drive_id: str = None):
        """
        Initializes the SharePointService with necessary configurations.
        """

        tenant_id = tenant_id or os.getenv("TENANT_ID", None)
        client_id = client_id or os.getenv("CLIENT_ID", None)
        client_secret = client_secret or os.getenv("CLIENT_SECRET", None)
        site_hostname = site_hostname or os.getenv("SITE_HOSTNAME", None)
        site_path = site_path or os.getenv("SITE_PATH", None)
        drive_name = drive_name or os.getenv("DRIVE_NAME", None)
        drive_id = drive_id or os.getenv("DRIVE_ID", None)
        if not tenant_id or not client_id or not client_secret or not site_hostname or not site_path:
            raise ValueError("All parameters (tenant_id, client_id, client_secret, site_hostname, site_path) must be provided or set in environment variables.")
        if not drive_name or not drive_id:
            raise ValueError("Drive name and drive ID must be provided or set in environment variables (DRIVE_NAME, DRIVE_ID).")
        
        self._impl = SharePointServiceImplementation(tenant_id=tenant_id,
                                                     client_id=client_id,
                                                     client_secret=client_secret,
                                                     site_hostname=site_hostname,
                                                     site_path=site_path,
                                                     drive_name=drive_name,
                                                     drive_id=drive_id)
    
    def retrieve_sharepoint_files_from_folder(self, folder_name: str) -> Dict[str, List[Dict[str, Any]]]:

        """
        Retrieve files from a specified folder in SharePoint.

        Args:
            folder_name (str): The name of the folder in SharePoint Document Library from which to fetch files.

        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary containing file information with the following structure:
                {
                    "files": [
                        {
                            "file-name": str,  # The name of the file
                            "file-id": str     # The unique ID of the file
                        },
                        ...
                    ]
                }

        Raises:
            Exception: If any error occurs while fetching files, such as issues with authentication, 
                       site ID retrieval, drive ID retrieval, or folder/file access.
        """

        return self._impl.retrieve_sharepoint_files_from_folder(folder_name)
    

    def download_file_from_sharepoint(self, file_id: str, target_folder: str):
        """
        Download a file from SharePoint using its file ID.

        Args:
            file_id (str): The ID of the file to download.

        Returns:
            bytes: The binary content of the downloaded file.

        Raises:
            Exception: If file download fails.
        """
        return self._impl.download_file_from_sharepoint(file_id, target_folder)
    

    def upload_file_to_sharepoint(self, file_path: str, target_folder: str):
        """
        Upload a file to SharePoint in the specified target folder.

        Args:
            file_path (str): The path to the file to be uploaded.
            target_folder (str): The folder path in SharePoint where the file will be uploaded.

        Returns:
            dict: The response JSON containing uploaded file information.

        Raises:
            Exception: If file upload fails.
        """
        return self._impl.upload_file_to_sharepoint(file_path, target_folder)
