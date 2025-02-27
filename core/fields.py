from django.db import models


class AzureSafeJSONField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, dict) or value is None:
            return value

        return super().from_db_value(value, expression, connection)
