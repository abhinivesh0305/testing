# connectors/cloud/azure/azure_blob.py

"""
This module provides a class for interacting with Azure Blob Storage.
"""

from .implementation import AzureBlobStorageImplementation

class AzureBlobStorage:
    """
    A class to handle Azure Blob Storage operations.
    """

    def __init__(self, connection_string):
        """
        Initialize the AzureBlobStorage with a connection string.

        :param connection_string: Azure Blob Storage connection string
        """
        self._impl = AzureBlobStorageImplementation(connection_string)

    def download_file(self, container_name, blob_name, target_folder_path):
        """
        Download a file from Azure Blob Storage to a local directory.

        :param container_name: Name of the Azure container
        :param blob_name: Name of the blob to download
        :param target_folder_path: Local directory to save the downloaded file
        """
        return self._impl.download_file(container_name, blob_name, target_folder_path)
