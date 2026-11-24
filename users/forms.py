from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from authentication.forms import INPUT_CLASSES
from authentication.models import validate_institutional_email

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "contact_number",
            "department",
            "institutional_id",
        )
        labels = {
            "department": "Institution / Department",
            "institutional_id": "Institutional ID",
        }
        help_texts = {
            "department": "Enter your institutional department or affiliation.",
            "institutional_id": "Enter your student or employee institutional ID.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["department"].widget.attrs["placeholder"] = (
            "e.g., Engineering or Student Affairs"
        )
        self.fields["institutional_id"].widget.attrs["placeholder"] = (
            "e.g., Student or employee ID"
        )
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_department(self):
        return self.cleaned_data["department"].strip()

    def clean_institutional_id(self):
        return self.cleaned_data["institutional_id"].strip()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        validate_institutional_email(email)
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already used by another account.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # login uses the email
        if commit:
            user.save()
        return user


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("role",)