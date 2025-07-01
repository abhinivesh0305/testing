import os
from .implementation import OpenAIConnectorImplementation

class OpenAIConnector:

    def __init__(self, openai_key: str = None):

        self._impl = OpenAIConnectorImplementation(openai_api_key=openai_key or os.getenv("OPENAI_API_KEY"))
        

    def connect_open_ai(self, modelname: str="gpt-4o-mini"):
        """
        Connects to the OpenAI API using the provided model name.

        Args:
            modelname (str): The name of the OpenAI model to use.

        Raises:
            ValueError: If the access key or model name is missing.
        """
        return self._impl.connect_open_ai(modelname=modelname)