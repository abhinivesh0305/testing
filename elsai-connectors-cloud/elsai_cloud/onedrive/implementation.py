"""
This module provides services to interact with OneDrive, including uploading, retrieving, and downloading files for a specific user.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from elsai_cloud.config.loggerConfig import setup_logger
from elsai_cloud.config.sharepoint_auth_service import get_access_token

class OneDriveServiceImplementation:
    """
    A service class to interact with OneDrive for file operations.
    """
    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None):
        self.tenant_id = tenant_id
        self.client_id= client_id
        self.client_secret = client_secret
        self.logger = setup_logger()

    def get_user_id(self, email: str) -> Optional[str]:
        try:
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            url = f"https://graph.microsoft.com/v1.0/users?$filter=userPrincipalName eq '{email}'"
            self.logger.info("Fetching user ID for email: %s", email)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            users = response.json().get('value', [])
            if users:
                user_id = users[0]['id']
                self.logger.info("User ID for %s: %s", email, user_id)
                return user_id
            self.logger.warning("User not found: %s", email)
            return None
        except Exception as e:
            self.logger.error("Failed to get user ID: %s", str(e))
            raise

    def upload_file_to_onedrive(self, email: str, local_file_path: str, folder_path: Optional[str] = None) -> str:
        try:
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            user_id = self.get_user_id(email)
            if not user_id:
                raise ValueError(f"User '{email}' not found.")

            file_name = os.path.basename(local_file_path)
            path = f"{folder_path}/{file_name}" if folder_path else file_name
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{path}:/content"
            
            self.logger.info("Uploading '%s' to OneDrive path: %s", file_name, path)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }

            with open(local_file_path, "rb") as f:
                response = requests.put(url, headers=headers, data=f, timeout=30)
                response.raise_for_status()

            self.logger.info("Upload successful: %s", path)
            return response.json().get("id")
        except Exception as e:
            self.logger.error("Upload failed: %s", str(e))
            raise

    def retrieve_onedrive_files_from_folder(self, email: str, folder_path: str) -> Dict[str, List[Dict[str, Any]]]:
        try:
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            user_id = self.get_user_id(email)
            if not user_id:
                raise ValueError(f"User '{email}' not found.")

            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root:/{folder_path}:/children"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            self.logger.info("Fetching files from OneDrive folder: %s", folder_path)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            files = response.json().get("value", [])
            files_info = [
                {"file-name": f["name"], "file-id": f["id"]}
                for f in files if "file" in f
            ]
            self.logger.info("Found %d file(s) in folder '%s'", len(files_info), folder_path)
            return {"files": files_info}
        except Exception as e:
            self.logger.error("Failed to retrieve files: %s", str(e))
            raise

    def download_file_from_onedrive(self, email: str, file_id: str, target_folder: str) -> str:
        try:
            access_token = get_access_token(tenant_id=self.tenant_id,client_id=self.client_id, client_secret=self.client_secret)
            user_id = self.get_user_id(email)
            if not user_id:
                raise ValueError(f"User '{email}' not found.")

            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            # Get file metadata (name)
            metadata_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/items/{file_id}"
            metadata_response = requests.get(metadata_url, headers=headers, timeout=10)
            metadata_response.raise_for_status()
            file_name = metadata_response.json().get("name")

            # Download file content
            download_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/items/{file_id}/content"
            response = requests.get(download_url, headers=headers, timeout=10)
            response.raise_for_status()

            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
                self.logger.info("Created target folder: %s", target_folder)

            local_path = os.path.join(target_folder, file_name)
            with open(local_path, 'wb') as f:
                f.write(response.content)

            self.logger.info("Downloaded file saved to: %s", local_path)
            return local_path
        except Exception as e:
            self.logger.error("Download failed: %s", str(e))
            raise
