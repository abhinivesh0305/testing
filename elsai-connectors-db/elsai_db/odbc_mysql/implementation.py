from elsai_db.config.base_sql_connector import BaseSQLConnector
from elsai_db.config.dialects import Dialects


class OdbcMysqlConnectorImplementation(BaseSQLConnector):
    """
    A connector class for ODBC MySQL databases..
    """
    def __init__(
            self, 
            llm,
            database_name: str = None,
            database_url: str = None,
            database_user: str = None,
            database_password: str = None,
            driver_name: str = None
        ):
        super().__init__(
            Dialects.ODBCMYSQL.value, llm, database_name, 
            database_url, database_user, database_password, driver_name
        )
