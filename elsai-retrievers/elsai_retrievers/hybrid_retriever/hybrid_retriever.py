from .implementation import HybridRetrieverImplementation
class HybridRetriever:
    """
    A class to perform hybrid retrieval using multiple retrievers, including BM25. 
    It combines their results using an ensemble approach and returns relevant documents.
    Attributes:
        logger: Logger instance for logging information and errors.
    """
    def __init__(self):
        """
        Initializes the HybridRetriever class and sets up logging.
        """
        self._impl = HybridRetrieverImplementation()

    def hybrid_retrieve(self, retrievers: list, question: str, chunks: list=None):
        """
        Performs a hybrid retrieval using BM25 and other retrievers, and returns the results.

        Args:
            chunks (list): List of text chunks to initialize BM25 retriever.
            retrievers (list): Existing list of retrievers to be used in the ensemble.
            question (str): The query or question to perform retrieval on.

        Returns:
            list: A list of relevant documents retrieved by the ensemble of retrievers.
        """
        return self._impl.hybrid_retrieve(retrievers, question, chunks)
