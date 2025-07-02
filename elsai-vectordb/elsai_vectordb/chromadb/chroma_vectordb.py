from .implementation import ChromaVectorDbImplementation
class ChromaVectorDb:
    def __init__(self, persist_directory: str = None):
        """
        Initializes the ChromaVectorDb class with the specified persistence directory.

        Args:
            persist_directory (str, optional): The directory path where ChromaDB will persist data. 
                                             Defaults to None, which will use environment variable or default path.
                                             
        """
        if persist_directory is None:
            persist_directory = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
        
        self._impl = ChromaVectorDbImplementation(persist_directory=persist_directory)

    def create_if_not_exists(self, collection_name: str):
        """
        Checks if a collection exists in ChromaDB, and creates it if it does not exist.

        Args:
            collection_name (str): The name of the collection to check or create.
        """
        self._impl.create_if_not_exists(collection_name)

    def add_document(self, document, collection_name: str) -> None:
        """
        Adds a document to a ChromaDB collection.

        Args:
            document (dict): A dictionary containing 'id', 'embeddings', 'page_content', and 'metadatas'.
            collection_name (str): The name of the collection to add the document to.
        """
        self._impl.add_document(document, collection_name)

    def retrieve_document(self, collection_name: str, embeddings: list, files_id: list=None, k: int = 10):
        """
        Retrieves documents from a ChromaDB collection based on the query embeddings and file IDs.

        Args:
            collection_name (str): The name of the collection to query.
            embeddings (list): The embeddings to use for the query.
            files_id (list): The list of file IDs to filter by.
            k (int, optional): The number of results to retrieve. Defaults to 10.

        Returns:
            dict: The results of the query.
        """
        return self._impl.retrieve_document(
            collection_name=collection_name,
            embeddings=embeddings,
            files_id=files_id,
            k=k)

    def get_collection(self, collection_name):
        """
        Retrieves a ChromaDB collection by name.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The ChromaDB collection.
        """
        return self._impl.get_collection(collection_name)

    def fetch_chunks(self, collection_name: str, files_id: list):
        """
        Fetches text chunks from the ChromaDB collection based on the collection name.

        Args:
            collection_name (str): The name of the collection to fetch data from.
            files_id (list): The list of file IDs to filter by.

        Returns:
            list: A list of text chunks from the collection.
        """
        return self._impl.fetch_chunks(collection_name, files_id)
    
    def delete_collection(self, collection_name: str):
        """
        Deletes a collection from ChromaDB.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        self._impl.delete_collection(collection_name)