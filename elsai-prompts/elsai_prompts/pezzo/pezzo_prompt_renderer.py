
from .implementation import PezzoPromptRendererImplementation
import os
class PezzoPromptRenderer:
    """
    A class to get prompts from Pezzo..
    """
    def __init__(
        self,
        api_key: str=None,
        project_id: str=None,
        environment: str=None,
        server_url: str=None,
    ):
        """
        api_key: str = Pezzo API key
        project_id: str = Pezzo project ID
        environment: str = Pezzo environment name
        server_url: str = Pezzo server host URL
        """
        self._impl = PezzoPromptRendererImplementation(
            api_key=api_key or os.getenv("PEZZO_API_KEY"),
            project_id=project_id or os.getenv("PEZZO_PROJECT_ID"),
            environment=environment or os.getenv("PEZZO_ENVIRONMENT"),
            server_url=server_url or os.getenv("PEZZO_SERVER_URL"),
        )

    def get_prompt(self, prompt_name: str) -> str:
        """
        Get a prompt from Pezzo using the prompt name.
        """
        return self._impl.get_prompt(prompt_name=prompt_name)
