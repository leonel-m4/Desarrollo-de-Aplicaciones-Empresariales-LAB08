from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/", include("quiz.urls")),
    path("api-auth/", include("rest_framework.urls")),
    # The contract: a machine-readable description of every API operation.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/", SpectacularSwaggerView.as_view(url_name="schema"),
        name="docs",
    ),
]
