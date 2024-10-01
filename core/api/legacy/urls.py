from django.urls import path

from core.api.legacy.views import ReportAPIView
from core.api.v1.views import ReportRetrieveAPIView

app_name = "legacy"


urlpatterns = [
    path(
        "reports/<int:report_id>/",
        ReportAPIView.as_view(),
        name="report_generation_api",
    ),
    path(
        "reports/result/<uuid:hash_id>/",
        ReportRetrieveAPIView.as_view(),
        name="report_result_api",
    ),
]
