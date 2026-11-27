from django.urls import path

from . import views

app_name = "incidents"

urlpatterns = [
    path("", views.incident_list, name="list"),
    path("new/", views.incident_create, name="new"),
    path("<int:pk>/", views.incident_detail, name="detail"),
    path("<int:pk>/status/", views.incident_status, name="status"),
]