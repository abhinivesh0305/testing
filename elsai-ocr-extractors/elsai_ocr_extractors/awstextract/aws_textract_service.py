from .implementation import AwsTextractConnectorImplementation
import os
class AwsTextractConnector:
    """
    A class to extract text from PDF files using AWS Textract after uploading to S3.
    It handles authentication, file upload, text extraction, and cleanup in AWS S3.
    """
    def __init__(self, access_key: str = None,
                 secret_key: str = None, session_token: str = None, region_name: str = "us-east-1"):
        

       

        access_key=access_key or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key=secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token=session_token or os.getenv("AWS_SESSION_TOKEN")
        region_name=region_name or os.getenv("AWS_REGION")

        if not access_key or not secret_key or not region_name:
            raise ValueError("AWS credentials, region must be provided. Environment variables can be used: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_REGION")
        self._impl = AwsTextractConnectorImplementation(access_key=access_key, secret_key=secret_key, session_token=session_token,region_name=region_name)

    
    def extract_text(self, file_path: str, s3_bucket: str = None, s3_folder: str = None):
        """
        Large files must be uploaded to S3 before extracting text using AWS Textract
        """
        s3_bucket = s3_bucket or os.getenv("S3_BUCKET")
        s3_folder = s3_folder or os.getenv("S3_FOLDER")
        return self._impl.extract_text(file_path=file_path, s3_bucket=s3_bucket, s3_folder=s3_folder)
    
    def extract_text_from_s3(self, s3_url: str):
        """
        Large files must be uploaded to S3 before extracting text using AWS Textract
        """
        #file_name = os.path.basename(file_path)
        #s3_key = f"{self.s3_folder}/{file_name}"
        
        return self._impl.extract_text_from_s3(s3_url=s3_url)
        
    def extract_text_features_from_s3(self, s3_url: str, features: list[str] = ["TABLES", "FORMS", "TEXT"]):
        """
        Extracts text and specified features from a PDF file stored in Amazon S3 using AWS Textract.

        Args:
            s3_url (str): The full S3 URL of the PDF file (e.g., "s3://bucket-name/path/to/file.pdf").
            features (List[str], optional): A list of Textract features to extract.
                                            Defaults to ["TABLES", "FORMS", "TEXT"].
                                            Valid options include "TABLES", "FORMS", and "TEXT".

        Returns:
            List: A list of Langchain Document objects, where each document contains the extracted text
                  and metadata (including the source S3 URL).

        Raises:
            Exception: If there is an error during the text extraction process.
        """
        return self._impl.extract_text_features_from_s3(s3_url=s3_url, features=features)

    def feature_mapping(self,features):
        return self._impl.feature_mapping(features=features)

    def async_process_document(self, s3_url, feature_list):
        """
        Starts asynchronous Textract analysis on a document in S3 with the specified features.

        Args:
            s3_url (str): The full S3 URL of the document to process
                           (e.g., "s3://your-bucket/your-document.pdf").
            feature_list (List[str]): A list of strings representing the Textract
                                       features to analyze (e.g., ["tables", "forms"]).

        Returns:
            str: The JobId of the asynchronous Textract analysis job.

        Raises:
            ValueError: If the provided feature list contains invalid feature strings.
            Exception: If there's an error starting the Textract analysis job.
        """
        
        return self._impl.async_process_document(s3_url=s3_url, feature_list=feature_list)

    