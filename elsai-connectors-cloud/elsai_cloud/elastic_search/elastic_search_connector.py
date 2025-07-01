import os
from .implementation import ElasticSearchConnectorImplementation
class ElasticSearchConnector:
    """
    A class to manage Elasticsearch connections and operations.
    """

    def __init__(self, cloud_url: str=None, api_key: str=None):
        """
        Initialize the Elasticsearch client with the provided cloud URL and API key.
        """
        cloud_url = cloud_url or os.getenv("ELASTIC_SEARCH_URL")
        api_key = api_key or os.getenv("ELASTIC_SEARCH_API_KEY")
        if not cloud_url or not api_key:
            raise ValueError("Elasticsearch cloud URL and API key must be provided or set in environment variables (ELASTIC_SEARCH_URL, ELASTIC_SEARCH_API_KEY).")
        self._impl = ElasticSearchConnectorImplementation(cloud_url, api_key)

    def add_document(self, index_name: str, document: dict, doc_id: str = None) -> dict:
        """
        Add a document to the specified index.
        """
        return self._impl.add_document(index_name, document, doc_id)

    def get_document(self, index_name: str, doc_id: str) -> dict:
        """
        Retrieve a document by its ID from the specified index.
        """
        return self._impl.get_document(index_name, doc_id)

    def search_documents(self, index_name: str, query: dict) -> list:
        """
        Search for documents in the specified index that match the query.
        """
        return self._impl.search_documents(index_name, query)
