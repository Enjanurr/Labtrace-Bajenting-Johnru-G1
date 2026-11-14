from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView, UpdateView
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import ProfileForm, UserRoleForm

User = get_user_model()
ADMIN = User.Role.ADMIN

class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile_edit.html"
    form_class = ProfileForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user  # no pk in the URL: users can only edit themselves

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


def _redirect_back(request, default="users:manage_list"):
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect(default)


@role_required(ADMIN)
def user_list_view(request):
    users = User.objects.all().order_by("username")
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    status = request.GET.get("status", "")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
    if role in User.Role.values:
        users = users.filter(role=role)
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)

    page_obj = Paginator(users, 15).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "users/user_list.html",
        {
            "page_obj": page_obj,
            "q": query,
            "role": role,
            "status": status,
            "roles": User.Role.choices,
            "querystring": query_params.urlencode(),
        },
    )


@require_POST
@role_required(ADMIN)
def change_role_view(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "You can't change your own role.")
    elif target.is_superuser:
        messages.error(request, "Superuser roles are managed in /admin/.")
    else:
        form = UserRoleForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{target.username} is now {target.get_role_display()}."
            )
        else:
            messages.error(request, "Invalid role.")
    return _redirect_back(request)


@require_POST
@role_required(ADMIN)
def toggle_active_view(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "You can't deactivate your own account here.")
    elif target.is_superuser:
        messages.error(request, "Superusers are managed in /admin/.")
    else:
        target.is_active = not target.is_active
        target.save(update_fields=["is_active"])
        state = "activated" if target.is_active else "deactivated"
        messages.success(request, f"{target.username} {state}.")
    return _redirect_back(request)