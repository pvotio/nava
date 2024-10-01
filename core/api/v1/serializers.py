import json
from urllib.parse import urljoin

from django.conf import settings
from rest_framework import serializers

from core.models import Report
from core.utils import generate_filename
from core.validators import validate_args


class WriteReportSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Report
        fields = ["id", "user", "hash_id", "template", "input_args"]
        read_only_fields = ["id", "hash_id"]

    def validate(self, attrs):
        status, missing_args = validate_args(attrs["template"].id, attrs["input_args"])
        if not status:
            raise serializers.ValidationError(
                {"input_args": f"Missing arguments: {', '.join(missing_args)}"}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        generated_report = Report(**validated_data)
        generated_report.output_file = generate_filename(
            generated_report.template.title
        )
        generated_report.save()
        return generated_report


class ReadReportSerializer(serializers.ModelSerializer):
    download_link = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()

    def get_download_link(self, obj):
        if obj.status == "G":
            return urljoin(settings.MEDIA_URL, f"{obj.output_file}.pdf")

        return None

    def get_error(self, obj):
        if obj.status == "F":
            try:
                error_message = json.loads(obj.output_content)["message"]
                return error_message
            except Exception:
                return obj.output_content

        return None

    class Meta:
        model = Report
        fields = [
            "id",
            "hash_id",
            "status",
            "error",
            "template",
            "input_args",
            "download_link",
        ]
        read_only_fields = fields
