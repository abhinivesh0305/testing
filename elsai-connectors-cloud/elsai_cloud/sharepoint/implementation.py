"""
This module provides services to interact with SharePoint, including retrieving and downloading files.
"""

from typing import Dict, List, Any
import os
import requests
from elsai_cloud.config.loggerConfig import setup_logger
from elsai_cloud.config.sharepoint_auth_service import get_access_token

class SharePointServiceImplementation:
    """
    A service class to interact with SharePoint for file retrieval and download.
    """

    GETTING_ACCESS_TOKEN_MSG = "Getting access token..." # nosec B105
    HTTP_ERROR_MSG = "HTTP error occurred: %s"
    UNEXPECTED_ERROR_MSG = "Unexpected error: %s"

    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None, site_hostname: str = None, site_path: str = None, drive_name: str = None, drive_id: str = None):
        self.logger = setup_logger()
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.site_hostname = site_hostname
        self.site_path = site_path
        self.drive_name = drive_name
        self.drive_id = drive_id
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
        try:
            # Step 1: Get Site ID
            self.logger.info(self.GETTING_ACCESS_TOKEN_MSG)
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            self.logger.info("Starting to retrieve files from SharePoint folder: %s", folder_name)
            self.logger.info("Fetching site information")

            site_hostname =self.site_hostname
            site_path = self.site_path
            site_url = f"https://graph.microsoft.com/v1.0/sites/{site_hostname}:{site_path}"
            headers = {"Authorization": f"Bearer {access_token}"}
            self.logger.info("Making GET request to %s for site info.", site_url)
            response = requests.get(site_url, headers=headers, timeout=10)
            response.raise_for_status()
            site_id = response.json()["id"]

            self.logger.info("Successfully retrieved site ID: %s", site_id)

            # Step 2: Get Drive ID
            self.logger.info("Fetching drives information.")
            drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
            response = requests.get(drives_url, headers=headers, timeout=10)
            response.raise_for_status()
            drives = response.json()["value"]
            
            self.logger.info("Drives available: %s", drives)
            drive_name = self.drive_name

            drive_id = next((drive["id"] for drive in drives if drive["name"] == drive_name), None)
            if not drive_id:
                self.logger.error("Drive '%s' not found in site '%s'.", drive_name, site_path)
                raise ValueError(f"Drive '{drive_name}' not found in site '{site_path}'.")

            self.logger.info("Found drive ID: %s for drive name: %s", drive_id, drive_name)

            # Step 3: Fetch Files in Folder
            self.logger.info("Fetching files in folder: %s", folder_name)
            folder_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_name}:/children"
            response = requests.get(folder_url, headers=headers, timeout=10)
            response.raise_for_status()
            files = response.json().get("value", [])
            if not files:
                self.logger.warning("No files found in folder: %s", folder_name)
            files_info = []
            for file in files:
                if file.get("file"):
                    file_name = file["name"]
                    file_id = file["id"]
                    files_info.append({
                        "file-name": file_name,
                        "file-id": file_id
                    })
                    self.logger.info("Found file: %s (ID: %s)", file_name, file_id)
            self.logger.info(
                "Successfully retrieved %d files from folder: %s",
                len(files_info), 
                folder_name
            )
            return {"files": files_info}
        except requests.exceptions.RequestException as e:
            self.logger.error(self.HTTP_ERROR_MSG, str(e))
            raise
        except ValueError as e:
            self.logger.error("Value error: %s", str(e))
            raise
        except Exception as e:
            self.logger.error(self.UNEXPECTED_ERROR_MSG, str(e))
            raise

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
        try:
            self.logger.info(self.GETTING_ACCESS_TOKEN_MSG)
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            headers = {"Authorization": f"Bearer {access_token}"}
            drive_id = self.drive_id
            download_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content"
            self.logger.info("Downloading file with ID: %s", file_id)
            
            response = requests.get(download_url, headers=headers, timeout=10)
            response.raise_for_status()
           
            self.logger.info("Writing file....")
            metadata_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}"
            metadata_response = requests.get(metadata_url, headers=headers, timeout=10)
            metadata_response.raise_for_status()
            file_name = metadata_response.json().get("name")
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
                self.logger.info("Created folder: %s", target_folder)
            local_file_path = os.path.join(target_folder, file_name)

            with open(local_file_path, 'wb') as f:
                f.write(response.content)
                self.logger.info("File Saved Successfully")
            return local_file_path
        
        except requests.exceptions.RequestException as e:
            self.logger.error(self.HTTP_ERROR_MSG, str(e))
            raise
        except Exception as e:
            self.logger.error(self.UNEXPECTED_ERROR_MSG, str(e))
            raise

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
        try:
            self.logger.info(self.GETTING_ACCESS_TOKEN_MSG)
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            drive_id = self.drive_id
            headers = {"Authorization": f"Bearer {access_token}"}
            self.logger.info("Locating target folder: %s", target_folder)
            folder_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{target_folder}"
            response = requests.get(folder_url, headers=headers, timeout=10)
            response.raise_for_status()
            folder_id = response.json()["id"]
            file_name = os.path.basename(file_path)
            self.logger.info("Uploading file: %s to folder ID: %s", file_name, folder_id)
            upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}:/{file_name}:/content"
            with open(file_path, 'rb') as file_content:
                response = requests.put(upload_url, headers=headers, data=file_content, timeout=10)
                response.raise_for_status()
                upload_response = response.json()
            self.logger.info("File uploaded successfully with ID: %s", upload_response.get("id", "Unknown"))
            return upload_response
        except requests.exceptions.RequestException as e:
            self.logger.error(self.HTTP_ERROR_MSG, str(e))
            raise
        except Exception as e:
            self.logger.error(self.UNEXPECTED_ERROR_MSG, str(e))
            raise
    
