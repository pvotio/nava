from django.urls import include, path

from core.views import ReportStatusTemplateView

urlpatterns = [
    path("api/v1/", include("core.api.v1.urls", namespace="v1")),
    # Legacy API
    path("api/", include("core.api.legacy.urls", namespace="legacy")),
    path(
        "reports/result/<uuid:hash_id>/",
        ReportStatusTemplateView.as_view(),
        name="report_result",
    ),
]
