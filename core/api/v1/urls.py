from django.urls import path

from core.api.v1.views import ReportCreateAPIView, ReportRetrieveAPIView

app_name = "v1"


urlpatterns = [
    path(
        "reports/create/",
        ReportCreateAPIView.as_view(),
        name="create_report",
    ),
    path(
        "reports/<uuid:hash_id>/",
        ReportRetrieveAPIView.as_view(),
        name="retrieve_report",
    ),
]
