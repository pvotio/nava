import logging
import time

import pandas as pd

from core.helper import get_template_by_pk
from service import exceptions
from service.database import mariadb, mssql, mysql, postgres

logger = logging.getLogger(__name__)


class Engine:
    def __init__(self, template_id):
        self.template = get_template_by_pk(template_id)
        self.init_database_class()

    def init_database_class(self):
        if self.template.database.backend == "MS":
            self.db = mssql.MSSQLDatabase(self.template.database.connection_string)
        elif self.template.database.backend == "PG":
            self.db = postgres.PostgreSQLDatabase(
                self.template.database.connection_string
            )
        elif self.template.database.backend == "MY":
            self.db = mysql.MySQLDatabase(self.template.database.connection_string)
        elif self.template.database.backend == "MA":
            self.db = mariadb.MariaDBDatabase(self.template.database.connection_string)
        else:
            raise ValueError(
                f"{self.template.database.backend} database is not supported"
            )

        try:
            self.db.connect()
        except Exception:
            logger.error(
                f"Failed to establish a connection with {self.template.database.name}"
            )
            raise exceptions.DatabaseConnectionError

    def read_sql(self, query, params=None, none_on_empty_df=False):
        for _ in range(3):
            try:
                self.db.connect()
                df = pd.read_sql_query(query, self.db.conn, params=params)
                if df.empty and none_on_empty_df:
                    return None
                return df
            except Exception as e:
                logger.error(f"Error executing query: {e}", exc_info=True)
                time.sleep(0.5)
        raise RuntimeError("Failed to execute query after 3 attempts.")

    def is_record_exist(self, query, params=None):
        self.db.connect()
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchone()
        return result is not None

    def close(self):
        self.db.close()
