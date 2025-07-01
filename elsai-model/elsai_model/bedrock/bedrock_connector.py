import os
from .implementation import BedrockConnectorImplementation

class BedrockConnector:

    def __init__(self, aws_access_key: str = None, 
                aws_secret_key: str = None,
                aws_session_token: str = None, 
                aws_region: str = None,
                max_tokens: int = 500,
                temperature: float = 0.1):
            self._impl = BedrockConnectorImplementation(
                aws_access_key=aws_access_key or os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_key=aws_secret_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=aws_session_token or os.getenv("AWS_SESSION_TOKEN", ""),
                aws_region=aws_region or os.getenv("AWS_REGION"),
                max_tokens=max_tokens,
                temperature=temperature or float(os.getenv("BEDROCK_TEMPERATURE", 0.1))
            )

    def connect_bedrock(self, model_id: str):
        """
        Connects to the AWS Bedrock API using the provided model ID..

        Args:
            model_id (str): The ID of the Bedrock model to use (e.g., 'anthropic.claude-v2', 'amazon.titan-text-express-v1').

        Raises:
            ValueError: If the AWS credentials, region, or model ID is missing.
        """

        return self._impl.connect_bedrock(model_id=model_id)