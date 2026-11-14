from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import TemplateView

from users.permissions import RoleRequiredMixin

User = get_user_model()

ROLE_HOME = {
    User.Role.ADMIN: "dashboard:admin",
    User.Role.INSTRUCTOR: "dashboard:instructor",
    User.Role.RESEARCHER: "dashboard:researcher",
    User.Role.STUDENT: "dashboard:student",
}


@login_required
def home(request):
    """Sends each user to the dashboard for their role."""
    return redirect(ROLE_HOME.get(request.user.role, "dashboard:student"))


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/admin.html"
    allowed_roles = [User.Role.ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_users"] = User.objects.count()
        ctx["student_count"] = User.objects.filter(role=User.Role.STUDENT).count()
        ctx["instructor_count"] = User.objects.filter(role=User.Role.INSTRUCTOR).count()
        ctx["researcher_count"] = User.objects.filter(role=User.Role.RESEARCHER).count()
        return ctx


class InstructorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/instructor.html"
    allowed_roles = [User.Role.INSTRUCTOR]


class ResearcherDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/researcher.html"
    allowed_roles = [User.Role.RESEARCHER]


class StudentDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/student.html"
    allowed_roles = [User.Role.STUDENT]