import json

from django.core.cache import cache
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.v1.serializers import WriteReportSerializer
from core.utils import get_cache_key


class ReportAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, report_id, format=None):
        args = dict(request.data)
        data = {
            "template": report_id,
            "input_args": {
                k: v[0] if isinstance(v, list) else v for k, v in args.items()
            },
        }
        report_hash_id = cache.get(get_cache_key(data, "create"))
        if not report_hash_id:
            serializer = WriteReportSerializer(data=data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                cache.set(
                    get_cache_key(data, "create"), json.dumps(serializer.data), 60 * 5
                )
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)

        return Response(json.loads(report_hash_id))
