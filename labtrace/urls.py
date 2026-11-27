from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="dashboard:home", permanent=False)),
    path("accounts/", include("authentication.urls")),
    path("dashboard/", include("dashboard.urls")),
    
    # Added in later steps:
    path("users/", include("users.urls")),
    path("visits/", include("access_logging.urls")),
    path("equipment/", include("equipment.urls")),
    path("incidents/", include("incidents.urls")),
]