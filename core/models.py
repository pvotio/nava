import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from core.utils import decrypt_connection_string, encrypt_connection_string
from core.validators import validate_python

User = get_user_model()


class Database(models.Model):
    BACKEND_CHOICES = (
        ("MS", "MSSQL"),
        ("PG", "Postgres"),
        ("MY", "MySQL"),
        ("MA", "MariaDB"),
    )
    name = models.CharField(max_length=200)
    backend = models.CharField(max_length=2, choices=BACKEND_CHOICES, default="MS")
    _connection_string = models.TextField(db_column="connection_string")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._connection_string:
            self._connection_string = decrypt_connection_string(self._connection_string)

    def save(self, *args, **kwargs):
        if hasattr(self, "_connection_string"):
            encrypted = encrypt_connection_string(self._connection_string).decode()
            self._connection_string = encrypted
        super().save(*args, **kwargs)

    @property
    def connection_string(self):
        return self._connection_string

    @connection_string.setter
    def connection_string(self, value):
        self._connection_string = encrypt_connection_string(value)

    def __str__(self):
        return self.name


class Template(models.Model):
    ORIENTATION_CHOICES = (("P", "Portrait"), ("L", "Landscape"))
    PAGE_SIZE_CHOICES = (
        ("A3", "A3"),
        ("A4", "A4"),
        ("A5", "A5"),
        ("Letter", "Letter"),
        ("Legal", "Legal"),
        ("Ledger", "Ledger"),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    database = models.ForeignKey(
        Database, blank=True, null=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    orientation = models.CharField(
        max_length=1, choices=ORIENTATION_CHOICES, default="L"
    )
    page_size = models.CharField(max_length=6, choices=PAGE_SIZE_CHOICES, default="A4")
    html_template = models.TextField(blank=False)
    python_script = models.TextField()
    python_validation_script = models.TextField()
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def clean(self):
        if not validate_python(str(self.python_script)):
            raise ValidationError("Detected potentially dangerous keyword or import")

        if not validate_python(str(self.python_validation_script)):
            raise ValidationError("Detected potentially dangerous keyword or import")

        return super().clean()


class Report(models.Model):
    STATUS_CHOICES = (
        ("P", "Pending"),
        ("F", "Failed"),
        ("G", "Generated"),
        ("D", "Deleted"),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    hash_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    template = models.ForeignKey(Template, on_delete=models.DO_NOTHING)
    input_args = models.JSONField(default=dict)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
    output_content = models.TextField(blank=True)
    output_file = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.output_file


class Argument(models.Model):
    report = models.ForeignKey(
        Template, on_delete=models.CASCADE, related_name="arguments"
    )
    name = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    optional = models.BooleanField(default=False)
    default_value = models.CharField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report.title}-{self.name}"

    def clean(self):
        if self.optional and not self.default_value:
            raise ValidationError("Default value must be set for optional arguments")

        if not self.optional and self.default_value:
            raise ValidationError("Required arguments don't take a default value")

        return super().clean()
