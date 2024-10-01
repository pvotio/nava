import logging

import mariadb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MariaDBDatabase:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None

    def connect(self):
        if not self.conn or not self.conn.open:
            connection_params = self.parse_connection_string(self.connection_string)
            self.conn = mariadb.connect(**connection_params)
            self.cursor = self.conn.cursor()
            logger.debug("Connected to the MariaDB database")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    @staticmethod
    def parse_connection_string(connection_string):
        params = {}
        for param in connection_string.split(";"):
            if param:
                key, value = param.split("=")
                params[key.strip()] = (
                    value.strip()
                    if key.strip().lower() != "port"
                    else int(value.strip())
                )
        return params
