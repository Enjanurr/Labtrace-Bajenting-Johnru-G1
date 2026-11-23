from django import forms
from authentication.forms import INPUT_CLASSES
from equipment.models import Room

from .models import LabVisit


class CheckInForm(forms.ModelForm):
    class Meta:
        model = LabVisit
        fields = ("room", "purpose")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = Room.objects.filter(is_active=True).order_by(
            "building", "name"
        )
        self.fields["room"].required = True
        self.fields["room"].empty_label = "Select a room"
        self.fields["room"].error_messages["invalid_choice"] = (
            "Select an active room from the list."
        )
        self.fields["purpose"].choices = [
            ("", "Select a purpose...")
        ] + list(LabVisit.Purpose.choices)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES