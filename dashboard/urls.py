from django.urls import path
from . import central
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", views.AdminDashboardView.as_view(), name="admin"),
    path("instructor/", views.InstructorDashboardView.as_view(), name="instructor"),
    path("researcher/", views.ResearcherDashboardView.as_view(), name="researcher"),
    path("student/", views.StudentDashboardView.as_view(), name="student"),
    path("central/", central.central_dashboard, name="central"),
    path("central/data/", central.central_data, name="central_data"),
    path("audit/", central.audit_trail, name="audit"),
    path("audit/api/", central.audit_api, name="audit_api"),
]