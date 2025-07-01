
import os
from .implementation import PostgreSQLConnectorImplementation

class PostgreSQLConnector:
    """
    A connector class for PostgreSQL databases.
    """
    def __init__(
            self, 
            llm,
            database_name: str = None,
            database_url: str = None,
            database_user: str = None,
            database_password: str = None,
        ):

        database_name = database_name or os.getenv("DB_NAME")
        database_url = database_url or os.getenv("DB_URL")
        database_user = database_user or os.getenv("DB_USER")
        database_password = database_password or os.getenv("DB_PASSWORD")
        if not database_name or not database_url or not database_user or not database_password:
            raise ValueError("Database name, URL, user, and password must be provided or set in environment variables (DB_NAME, DB_URL, DB_USER, DB_PASSWORD).")
        
        self._impl = PostgreSQLConnectorImplementation(
            llm, 
            database_name, 
            database_url, 
            database_user, 
            database_password
        )
        
    def invoke(self, query: str):
        return self._impl.invoke(query)