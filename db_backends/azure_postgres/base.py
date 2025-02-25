import logging

import psycopg2
from azure.identity import DefaultAzureCredential
from django.conf import settings
from django.db.backends.postgresql.base import \
    DatabaseWrapper as BaseDatabaseWrapper


logger = logging.getLogger(__name__)


class DatabaseWrapper(BaseDatabaseWrapper):
    def get_new_connection(self, conn_params):
        """Override connection method to support both authentication types."""

        if settings.SQL_AD_LOGIN:
            logger.info("POSTGRES AD LOGIN AUTH")
            credential = DefaultAzureCredential()
            token = credential.get_token(
                "https://ossrdbms-aad.database.windows.net/.default"
            ).token
            logger.info(f"FETCHED TOKEN FROM AZURE: {token}")
            conn_params["password"] = token
            conn_params["user"] = settings.DATABASES["default"]["USER"]
            conn_params["sslmode"] = "require"
        else:
            conn_params["user"] = settings.DATABASES["default"]["USER"]
            conn_params["password"] = settings.DATABASES["default"]["PASSWORD"]

        return psycopg2.connect(**conn_params)
