from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse

from access_logging.models import LabVisit
from equipment.models import EquipmentLog

from .forms import LoginForm, RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created for {user.username}. You can now sign in.",
            )
            return redirect("authentication:login")
    else:
        form = RegistrationForm()

    return render(request, "authentication/register.html", {"form": form})


class LabTraceLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  # logged-in users skip the login page

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.first_name or user.username}!")
        return super().form_valid(form)  # honors a safe ?next= param, else LOGIN_REDIRECT_URL


class LabTraceLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            active_visits = LabVisit.objects.filter(
                user=request.user,
                status=LabVisit.Status.ACTIVE,
            )
            open_logs = EquipmentLog.objects.filter(
                visit__user=request.user,
                returned_at__isnull=True,
            ).select_related("asset", "visit")

            if active_visits.exists() or open_logs.exists():
                parts = []
                if active_visits.exists():
                    visit = active_visits.first()
                    parts.append(
                        f"active lab visit at {visit.lab_location} "
                        f"(check out here: {reverse('access_logging:my_visits')})"
                    )
                if open_logs.exists():
                    assets = ", ".join(
                        f"{log.asset.asset_code} - {log.asset.name}"
                        for log in open_logs
                    )
                    parts.append(
                        f"unreturned equipment: {assets} "
                        f"(return them here: {reverse('equipment:mine')})"
                    )
                messages.warning(
                    request,
                    "Logout blocked. Please resolve the following first: " +
                    "; ".join(parts),
                )
                return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)