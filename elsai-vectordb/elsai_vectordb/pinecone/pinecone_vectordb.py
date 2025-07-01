from .implementation import PineconeVectorDbImplementation
import os
class PineconeVectorDb:
    """
    PineconeVectorDb handles operations for managing and querying vectors in Pinecone.
    
    Key Methods:
    1. __init__() - Initializes Pinecone index, creating it if necessary.
    2. add_document() - Adds or updates documents in the Pinecone index.
    3. retrieve_document() - Retrieves relevant documents from the index based on embeddings and filters.
    """

    def __init__(self, index_name: str, pinecone_api_key=None, dimension: int = 1536):
        """
        Initializes the PineconeVectorDb and ensures the index exists. If the index does not exist,
        it is created with the specified dimension.

        Args:
            index_name (str): The name of the Pinecone index to use.
            dimension (int): Dimensionality of the embeddings. Default is 1536.

        Raises:
            Exception: If Pinecone index creation or initialization fails.
        """

        api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("Pinecone API key must be provided either as an argument or through the environment variable 'PINECONE_API_KEY'.")
        
        self._impl = PineconeVectorDbImplementation(index_name=index_name, pinecone_api_key=api_key, dimension=dimension)
    
    def add_document(self, document: dict, namespace: str) -> None:
        """
        Adds a document to the Pinecone index. If the document already exists, it is updated.

        Args:
            document (dict): A dictionary containing the document ID, embeddings, and optional metadata.
            namespace (str): The namespace to add the document to.
        Raises:
            ValueError: If the document lacks required fields ('id' or 'embeddings').
            RuntimeError: If the document insertion fails for any reason.
        """
        self._impl.add_document(document=document, namespace=namespace) 

    def retrieve_document(self, namespace:str, question_embedding: list, files_id: list=None, k: int = 10):
        """
        Retrieves documents from the Pinecone index by querying with embeddings and applying a file ID filter.

        Args:
            namespace (str): The namespace to query for documents.
            question_embedding (list): Embeddings to use for the similarity search.
            files_id (list): List of file IDs to filter results by.
            k (int): The number of top results to retrieve. Default is 10.

        Returns:
            dict: A dictionary of matching documents along with their metadata.

        Raises:
            Exception: If the query operation fails.
        """
        return self._impl.retrieve_document(
            namespace=namespace,
            question_embedding=question_embedding,
            files_id=files_id,
            k=k
        )
