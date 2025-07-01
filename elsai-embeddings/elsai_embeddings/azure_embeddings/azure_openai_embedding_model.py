import os
from .implementation import AzureOpenAIEmbeddingModelImplementation

class AzureOpenAIEmbeddingModel:
    """
    Class for embedding text and documents using Azure OpenAI Embeddings API.
    """
    def __init__(
            self,
            model: str = 'text-embedding-ada-002',
            azure_deployment: str = None,
            azure_endpoint: str = None,
            azure_api_key: str = None,
            azure_api_version: str = None
        ):
        azure_deployment = azure_deployment or os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
        azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = azure_api_key or os.getenv("AZURE_OPENAI_API_KEY")
        azure_api_version = azure_api_version or os.getenv("OPENAI_API_VERSION")

        missing = []
        if not azure_deployment:
            missing.append("'azure_deployment' (env var: AZURE_EMBEDDING_DEPLOYMENT_NAME)")
        if not azure_endpoint:
            missing.append("'azure_endpoint' (env var: AZURE_OPENAI_ENDPOINT)")
        if not azure_api_key:
            missing.append("'azure_api_key' (env var: AZURE_OPENAI_API_KEY)")
        if not azure_api_version:
            missing.append("'azure_api_version' (env var: OPENAI_API_VERSION)")

        if missing:
            raise ValueError(
                f"The following required parameters are missing: {', '.join(missing)}. "
                "Please provide them as arguments or set the corresponding environment variables."
            )

        self._impl = AzureOpenAIEmbeddingModelImplementation(
            model=model,
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_api_key,
            azure_api_version=azure_api_version
        )

    def embed_query(self, text: str) -> list:
        """Embeds the given text using Azure OpenAI's embed_query method,
          returning the embedding vector.
        """
        return self._impl.embed_query(text)
    def embed_documents(self, texts: list) -> list:
        """Embeds the given list of texts using Azure OpenAI's embed_documents method,
          returning the embedding vectors.
        """
        return self._impl.embed_documents(texts)

    def get_embedding_model(self):
        """Returns the Azure OpenAI embedding model."""
        return self._impl.azure_embeddings_model
