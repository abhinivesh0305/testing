from typing import List, Dict, Any, Optional
from .implementation import OneDriveServiceImplementation
import os

class OneDriveService:
    """
    A service class to interact with OneDrive for file operations.
    """
    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None):
        tenant_id = tenant_id or os.getenv("TENANT_ID", None)
        client_id = client_id or os.getenv("CLIENT_ID", None)
        client_secret = client_secret or os.getenv("CLIENT_SECRET", None)

        if not tenant_id or not client_id or not client_secret:
            raise ValueError("All parameters (tenant_id, client_id, client_secret) must be provided or set in environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET).")
        self._impl = OneDriveServiceImplementation(tenant_id=tenant_id,client_id=client_id, client_secret=client_secret)

    def get_user_id(self, email: str) -> Optional[str]:
        return self._impl.get_user_id(email)

    def upload_file_to_onedrive(self, email: str, local_file_path: str, folder_path: Optional[str] = None) -> str:
        return self._impl.upload_file_to_onedrive(email, local_file_path, folder_path)

    def retrieve_onedrive_files_from_folder(self, email: str, folder_path: str) -> Dict[str, List[Dict[str, Any]]]:
        return self._impl.retrieve_onedrive_files_from_folder(email, folder_path)

    def download_file_from_onedrive(self, email: str, file_id: str, target_folder: str) -> str:
        return self._impl.download_file_from_onedrive(email, file_id, target_folder)
