import logging

import psycopg2
from azure.identity import DefaultAzureCredential
from django.conf import settings
from django.db.backends.postgresql.base import \
    DatabaseWrapper as BaseDatabaseWrapper

logger = logging.getLogger(__name__)
_azure_credential = None


def get_azure_credential():
    global _azure_credential
    if _azure_credential is None:
        _azure_credential = DefaultAzureCredential()

    return _azure_credential


class DatabaseWrapper(BaseDatabaseWrapper):
    def get_new_connection(self, conn_params):
        """Override connection method to support both authentication types."""

        if settings.SQL_AD_LOGIN:
            logger.debug("Postgres AD Login")
            credential = get_azure_credential()
            token = credential.get_token(
                "https://ossrdbms-aad.database.windows.net/.default"
            ).token
            logger.debug(f"Fetched token from Azure: {token[:20]}[DEDUCTED]")
            conn_params["password"] = token
            conn_params["user"] = settings.DATABASES["default"]["USER"]
            conn_params["sslmode"] = "require"
        else:
            logger.debug("Postgres Basic Login")
            conn_params["user"] = settings.DATABASES["default"]["USER"]
            conn_params["password"] = settings.DATABASES["default"]["PASSWORD"]

        return psycopg2.connect(**conn_params)
