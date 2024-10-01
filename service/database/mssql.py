import logging

import pyodbc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MSSQLDatabase:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None

    def connect(self):
        if not self.conn or self.conn.closed:
            self.conn = pyodbc.connect(self.connection_string, autocommit=True)
            self.cursor = self.conn.cursor()
            logger.debug("Connected to the MSSQL database")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
