from django import forms

from access_logging.models import LabVisit
from equipment.models import EquipmentLog

from .models import Incident
from .services import allowed_next_statuses

INPUT = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
)
def style(form):
    for field in form.fields.values():
        field.widget.attrs["class"] = INPUT


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ("title", "category", "severity", "visit", "equipment_log", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}
        labels = {"visit": "Related lab visit", "equipment_log": "Related equipment loan"}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        # Only the reporter's own visits / loans can be linked.
        self.fields["visit"].queryset = LabVisit.objects.filter(user=user).order_by("-pk")
        self.fields["equipment_log"].queryset = (
            EquipmentLog.objects.filter(visit__user=user).order_by("-pk")
        )
        self.fields["visit"].required = False
        self.fields["equipment_log"].required = False
        self.fields["visit"].empty_label = "— Not linked to a visit —"
        self.fields["equipment_log"].empty_label = "— No equipment involved —"
        style(self)


class StatusUpdateForm(forms.Form):
    status = forms.ChoiceField(label="Move to")
    note = forms.CharField(
        label="Note", required=False, widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Required when resolving.",
    )

    def __init__(self, *args, incident, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (s.value, s.label) for s in allowed_next_statuses(incident, user)
        ]
        style(self)

    def clean(self):
        data = super().clean()
        if data.get("status") == Incident.Status.RESOLVED and not data.get("note", "").strip():
            self.add_error("note", "Resolution notes are required to resolve an incident.")
        return data