import os
from .implementation import AzureOpenAIConnectorImplementation
class AzureOpenAIConnector:

    def __init__(self, azure_endpoint: str = None, openai_api_key: str = None, openai_api_version: str = None, temperature: float = 0.1):
        self._impl = AzureOpenAIConnectorImplementation(azure_endpoint=azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", None),
                                                        openai_api_key=openai_api_key or os.getenv("AZURE_OPENAI_API_KEY", None),
                                                        openai_api_version=openai_api_version or os.getenv("OPENAI_API_VERSION", None),
                                                        temperature=temperature or float(os.getenv("AZURE_OPENAI_TEMPERATURE", 0.1)))

    def connect_azure_open_ai(self, deploymentname: str):
        """
        Connects to the Azure OpenAI API using the provided model name.

        Args:
            deploymentname (str): The name of the OpenAI model to use.

        Raises:
            ValueError: If the endpoint, API key, or model name is missing.
        """

        return self._impl.connect_azure_open_ai(deploymentname=deploymentname)

