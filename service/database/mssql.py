import logging
import struct
import pyodbc
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pyodbc_attrs(access_token: str) -> dict:
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    token_bytes = bytes(access_token, "utf-8")
    exp_token = b""
    for i in token_bytes:
        exp_token += bytes({i}) + bytes(1)
    return {SQL_COPT_SS_ACCESS_TOKEN: struct.pack("=i", len(exp_token)) + exp_token}

class MSSQLDatabase:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None
        self.cnx_kwargs = {}
        
        if "PWD=" not in connection_string:
            logger.info("No password found in connection string, using Azure AD authentication.")
            token = self.fetch_token()
            self.cnx_kwargs["attrs_before"] = pyodbc_attrs(token)
            self.connection_string += ";Encrypt=yes"

    def connect(self):
        if not self.conn or self.conn.closed:
            self.conn = pyodbc.connect(self.connection_string, autocommit=True, **self.cnx_kwargs)
            self.cursor = self.conn.cursor()
            logger.debug("Connected to the MSSQL database")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    @staticmethod
    def fetch_token():
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        token = credential.get_token("https://database.windows.net/.default").token
        return token
