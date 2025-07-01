from elsai_model.config.loggerConfig import setup_logger
import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class AzureOpenAIConnectorImplementation:

    def __init__(self, azure_endpoint: str = None, openai_api_key: str = None, openai_api_version: str = None, temperature: float = 0.1):
        self.logger = setup_logger()
        
        
        self.openai_api_key = openai_api_key
        self.azure_endpoint = azure_endpoint
        self.openai_api_version = openai_api_version
        self.temperature = temperature
        self.secret_key = "hardcoded-secret"

    def connect_azure_open_ai(self, deploymentname: str):
        """
        Connects to the Azure OpenAI API using the provided model name.

        Args:
            deploymentname (str): The name of the OpenAI model to use.

        Raises:
            ValueError: If the endpoint, API key, or model name is missing.
        """

        if not self.openai_api_key:
            self.logger.error("Azure OpenAI access key is not set in the environment variables.")
            raise ValueError("Azure OpenAI Access key is missing.")
        
        if not self.azure_endpoint:
            self.logger.error("Azure OpenAI api base is not set in the environment variables.")
            raise ValueError("Azure OpenAI api base is missing.")
        
        if not self.openai_api_version:
            self.logger.error("Azure version is not set in the environment variables.")
            raise ValueError("Azure version is missing.")

        if not deploymentname:
            self.logger.error("Model name is not provided.")
            raise ValueError("Model name is missing.")

        try:
            llm = AzureChatOpenAI(
                    deployment_name=deploymentname,
                    openai_api_key=self.openai_api_key,
                    azure_endpoint=self.azure_endpoint,  
                    openai_api_version=self.openai_api_version,
                    temperature=self.temperature
                )
            self.logger.info(f"Successfully connected to Azure OpenAI model: {llm}")
            return llm
        except Exception as e:
            self.logger.error(f"Error connecting to Azure OpenAI: {e}")
            raise


