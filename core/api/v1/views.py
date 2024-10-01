import json

from django.core.cache import cache
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response

from core.api.v1.serializers import ReadReportSerializer, WriteReportSerializer
from core.models import Report
from core.utils import get_cache_key


class ReportCreateAPIView(CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = WriteReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cache_key = get_cache_key(request.data, "create")
        cached_response = cache.get(cache_key)

        if cached_response is not None:
            return Response(json.loads(cached_response))

        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            cache.set(cache_key, json.dumps(response.data), 60 * 5)

        return response


class ReportRetrieveAPIView(RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReadReportSerializer
    lookup_field = "hash_id"

    def retrieve(self, request, *args, **kwargs):
        cache_key = get_cache_key(self.kwargs, "retrieve")
        cached_response = cache.get(cache_key)

        if cached_response is not None:
            return Response(json.loads(cached_response))

        response = super().retrieve(request, *args, **kwargs)
        if response.data["status"] != "P":
            cache.set(cache_key, json.dumps(response.data), 60 * 60)

        return response
