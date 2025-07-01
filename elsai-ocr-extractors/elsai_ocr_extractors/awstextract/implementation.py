import os
import boto3
from elsai_ocr_extractors.config.loggerConfig import setup_logger
from langchain_community.document_loaders import AmazonTextractPDFLoader
from textractor import Textractor
from textractor.data.constants import TextractFeatures
import time
class AwsTextractConnectorImplementation:
    """
    A class to extract text from PDF files using AWS Textract after uploading to S3.
    It handles authentication, file upload, text extraction, and cleanup in AWS S3.
    """
    def __init__(self, access_key: str = None,
                 secret_key: str = None, session_token: str = None, region_name: str = "us-east-1"):
        self.textract_client = boto3.client(
            "textract",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            region_name=region_name
        )
        self.extractor = Textractor(region_name=region_name)
        self.s3_connector = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
        )
        self.logger = setup_logger()
        


    def upload_file_to_s3(self, bucket_name: str, s3_key: str, file_path: str):
        """
        Uploads a file to an S3 bucket.
        """
        try:
            self.s3_connector.upload_file(file_path, bucket_name, s3_key)
            self.logger.info("File %s uploaded successfully to %s", file_path, s3_key)
            s3_uri = f"s3://{bucket_name}/{s3_key}"
            return s3_uri
        except Exception as e:
            self.logger.error("Error uploading file: %s", e)
            raise e
           
    def delete_file_from_s3(self, bucket_name: str, s3_key: str):
        """
        Deletes a file from an S3 bucket.
        """
        try:
            self.s3_connector.delete_object(Bucket=bucket_name, Key=s3_key)
            self.logger.info("File %s deleted successfully from %s", s3_key, bucket_name)
        except Exception as e:
            self.logger.error("Error deleting file: %s", e)
            raise e

    def extract_text(self, file_path: str, s3_bucket: str = None, s3_folder: str = None):
        """
        Large files must be uploaded to S3 before extracting text using AWS Textract
        """
        if not s3_bucket:
            raise ValueError("S3 bucket must be specified. Environment variables can be used: S3_BUCKET")
        file_name = os.path.basename(file_path)
        
        s3_key = f"{s3_folder}/{file_name}"
        s3_uri = self.upload_file_to_s3(s3_bucket, s3_key, file_path)
        try:
            self.logger.info("Extracting text from %s using AWS Textract", s3_uri)
            loader = AmazonTextractPDFLoader(s3_uri, client=self.textract_client)
            documents =  loader.load()
            return documents
        except Exception as e:
            self.logger.error("Error extracting text: %s", e)
            raise e
        finally:
            self.delete_file_from_s3(s3_bucket, s3_key)
    
    def extract_text_from_s3(self, s3_url: str):
        """
        Large files must be uploaded to S3 before extracting text using AWS Textract
        """
        
        try:
            self.logger.info("Extracting text from %s using AWS Textract", s3_url)
            loader = AmazonTextractPDFLoader(s3_url, client=self.textract_client)
            loader.textract_features = ["TABLES"]
            documents =  loader.load()
            return documents
        except Exception as e:
            self.logger.error("Error extracting text: %s", e)
            raise e
        
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
        try:
            self.logger.info(f"Extracting text and features '{features}' from %s using AWS Textract", s3_url)
            loader = AmazonTextractPDFLoader(s3_url, client=self.textract_client)
            # Set the Textract features to extract based on the provided 'features' argument.
            loader.textract_features = features
            # Load the documents from the S3 URL using the configured features.
            documents = loader.load()
            return documents
        except Exception as e:
            self.logger.error("Error extracting text and features from %s: %s", s3_url, e)
            raise e

    def feature_mapping(self,features):
        textract_feature_list = []
        feature_mapping = {
            "tables": TextractFeatures.TABLES,
            "forms": TextractFeatures.FORMS,
            "layout": TextractFeatures.LAYOUT,
        }
        for feature_string in features:
            if feature_string.lower() in feature_mapping:
                textract_feature_list.append(feature_mapping[feature_string.lower()])
            else:
                raise ValueError(f"Invalid Textract feature string: '{feature_string}'. "
                                f"Valid options are: {list(feature_mapping.keys())}")
        return textract_feature_list

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
        
        textract_features = self.feature_mapping(feature_list)
        # Start asynchronous Textract analysis using Textractor
        
        document = self.extractor.start_document_analysis(
            file_source=s3_url,
            features=textract_features,
            save_image=False
        )
        job_id = document.job_id
        

        # Poll job status
        start_time = time.time()
        while True:
            time.sleep(1)
            response = self.textract_client.get_document_analysis(JobId=job_id)
            status = response['JobStatus']

            if status == 'SUCCEEDED':
                break
            elif status in ['FAILED', 'PARTIAL_SUCCESS']:
                raise RuntimeError(f"Textract job failed: {status}")
            elif time.time() - start_time > 300:
                raise TimeoutError("Textract job timed out.")

        # Handle pagination
        blocks = response.get('Blocks', [])
        next_token = response.get('NextToken')
        while next_token:
            paginated = self.textract_client.get_document_analysis(JobId=job_id, NextToken=next_token)
            blocks += paginated.get('Blocks', [])
            next_token = paginated.get('NextToken')
        response['Blocks'] = blocks
        return response
    

    