import os
from .implementation import SQLiteConnectorImplementation
class SQLiteConnector:
    """
    A connector class for sqlite3 databases.
    """

    def __init__(self, llm, database_path:str = None):

        database_path = database_path or os.getenv("DB_PATH")
        if not database_path:
            raise ValueError("Database path must be provided or set in the environment variable (DB_PATH).")
        
        self._impl = SQLiteConnectorImplementation(llm, database_path=database_path)
        
    
    def invoke(self, query: str):
        return self._impl.invoke(query)