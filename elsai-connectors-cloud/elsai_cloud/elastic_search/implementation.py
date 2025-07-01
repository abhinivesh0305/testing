import os
from elsai_cloud.config.loggerConfig import setup_logger
from elasticsearch import Elasticsearch, NotFoundError
class ElasticSearchConnectorImplementation:
    """
    A class to manage Elasticsearch connections and operations.
    """

    def __init__(self, cloud_url: str = None, api_key: str = None):
        """
        Initialize the Elasticsearch client with the provided cloud URL and API key.
        """
        self.logger = setup_logger()
        try:
            self.es = Elasticsearch(cloud_url, api_key=api_key)
            if self.es.ping():
                self.logger.info("Connected to Elasticsearch!")
            else:
                self.logger.error("Elasticsearch ping failed.")
                raise ValueError("Connection failed.")
        except Exception as e:
            self.logger.error(f"Elasticsearch connection error: {e}")
            raise

    def add_document(self, index_name: str, document: dict, doc_id: str = None) -> dict:
        """
        Add a document to the specified index.
        """
        try:
            response = self.es.index(index=index_name, id=doc_id, document=document)
            self.logger.info(f"Document added to index '{index_name}' with ID '{response['_id']}'.")
            return response
        except Exception as e:
            self.logger.error(f"Error adding document to index '{index_name}': {e}")
            raise

    def get_document(self, index_name: str, doc_id: str) -> dict:
        """
        Retrieve a document by its ID from the specified index.
        """
        try:
            response = self.es.get(index=index_name, id=doc_id)
            self.logger.info(f"Document retrieved from index '{index_name}' with ID '{doc_id}'.")
            return response['_source']
        except NotFoundError:
            self.logger.warning(f"Document with ID '{doc_id}' not found in index '{index_name}'.")
            raise ValueError(f"Document with ID '{doc_id}' not found in index '{index_name}'.")
        except Exception as e:
            self.logger.error(f"Error retrieving document from index '{index_name}': {e}")
            raise

    def search_documents(self, index_name: str, query: dict) -> list:
        """
        Search for documents in the specified index that match the query.
        """
        try:
            response = self.es.search(index=index_name, query=query)
            hits = response['hits']['hits']
            self.logger.info(f"Search in index '{index_name}' returned {len(hits)} hits.")
            return hits
        except Exception as e:
            self.logger.error(f"Error searching documents in index '{index_name}': {e}")
            raise

