from elsai_model.config.loggerConfig import setup_logger
import os
from langchain_aws.chat_models import ChatBedrockConverse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class BedrockConnectorImplementation:

    def __init__(self, aws_access_key: str = None, 
                 aws_secret_key: str = None, 
                 aws_region: str = None,
                 aws_session_token: str = None,
                 max_tokens:int = 500,  # Maximum number of tokens to generate per request
                 temperature: float = 0.1):
        
        self.logger = setup_logger()
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.aws_session_token = aws_session_token

    def connect_bedrock(self, model_id: str=""):
        """
        Connects to the AWS Bedrock API using the provided model ID.

        Args:
            model_id (str): The ID of the Bedrock model to use (e.g., 'anthropic.claude-v2', 'amazon.titan-text-express-v1').

        Raises:
            ValueError: If the AWS credentials, region, or model ID is missing.
        """

        if not self.aws_access_key:
            self.logger.error("AWS access key ID is not set in the environment variables.")
            raise ValueError("AWS access key ID is missing.")
        
        if not self.aws_secret_key:
            self.logger.error("AWS secret access key is not set in the environment variables.")
            raise ValueError("AWS secret access key is missing.")
        
        if not self.aws_region:
            self.logger.error("AWS region is not set in the environment variables.")
            raise ValueError("AWS region is missing.")

        if not model_id:
            self.logger.error("Model ID is not provided.")
            raise ValueError("Model ID is missing.")

        try:
            llm = ChatBedrockConverse(
        model_id=model_id,
        region_name=self.aws_region,  # Match your Bedrock setup
        temperature=self.temperature,
        max_tokens=self.max_tokens,
        aws_access_key_id=self.aws_access_key,
        aws_secret_access_key=self.aws_secret_key,
        aws_session_token=self.aws_session_token
    )
            self.logger.info(f"Successfully connected to AWS Bedrock model: {model_id}")
            return llm
        except Exception as e:
            self.logger.error(f"Error connecting to AWS Bedrock: {e}")
            raise