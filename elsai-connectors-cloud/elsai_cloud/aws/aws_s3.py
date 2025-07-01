"""
This module provides a connector for AWS S3 using boto3.
"""

from .implementation import AwsS3ConnectorImplementation
import os

class AwsS3Connector:
    """
    A connector class for interacting with AWS S3.
    """

    def __init__(self, access_key: str = None, secret_key: str = None, session_token: str = None):
        """
        Initializes the S3Connector with AWS credentials.

        :param access_key: AWS access key ID
        :param secret_key: AWS secret access key
        :param session_token: AWS session token
        """

        access_key = access_key or os.getenv("AWS_ACCESS_KEY_ID", None)
        secret_key = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY", None)
        session_token = session_token or os.getenv("AWS_SESSION_TOKEN", None)
        if not access_key or not secret_key:
            raise ValueError("AWS access key and secret key must be provided or set in environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).")
        self._impl = AwsS3ConnectorImplementation(access_key, secret_key, session_token)

    def upload_file_to_s3(self, bucket_name: str, s3_key: str, file_path: str):
        """
        Uploads a file to an S3 bucket.

        :param bucket_name: Name of the S3 bucket
        :param s3_key: Key to store the file under in the bucket
        :param file_path: Path to the file to upload
        """
        return self._impl.upload_file_to_s3(bucket_name, s3_key, file_path)

    def delete_file_from_s3(self, bucket_name: str, s3_key: str):
        """
        Deletes a file from an S3 bucket.

        :param bucket_name: Name of the S3 bucket
        :param s3_key: Key of the file to delete
        """
        return self._impl.delete_file_from_s3(bucket_name, s3_key)

    def download_file_from_s3(self, bucket_name: str, file_name: str, download_path: str):
        """
        Downloads a file from an S3 bucket to a specified local path.

        :param bucket_name: Name of the S3 bucket
        :param file_name: Name of the file to download
        :param download_path: Local path to download the file to
        """
        return self._impl.download_file_from_s3(bucket_name, file_name, download_path)
