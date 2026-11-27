from django import forms

from authentication.forms import INPUT_CLASSES

from .models import Asset, Condition, EquipmentLog

class BorrowForm(forms.ModelForm):
    class Meta:
        model = EquipmentLog
        fields = ("asset", "pre_condition", "pre_condition_notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset"].queryset = Asset.objects.filter(
            availability_status=Asset.Availability.AVAILABLE
        ).order_by("asset_code")
        self.fields["asset"].empty_label = "Select equipment..."

        # You can't borrow something that is already missing.
        self.fields["pre_condition"].choices = [("", "Select condition...")] + [
            c for c in Condition.choices if c[0] != Condition.MISSING
        ]
        self.fields["pre_condition"].label = "Condition before borrowing"
        self.fields["pre_condition_notes"].label = "Condition notes (optional)"
        self.fields["pre_condition_notes"].required = False
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES


class ReturnForm(forms.ModelForm):
    class Meta:
        model = EquipmentLog
        fields = ("post_condition", "post_condition_notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["post_condition"].required = True
        self.fields["post_condition"].choices = [
            ("", "Select condition...")
        ] + list(Condition.choices)
        self.fields["post_condition"].label = "Condition on return"
        self.fields["post_condition_notes"].label = "Condition notes (optional)"
        self.fields["post_condition_notes"].required = False
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ("asset_code", "name", "availability_status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status = self.fields["availability_status"]
        if self.instance.pk and self.instance.availability_status == Asset.Availability.BORROWED:
            # Borrowed status is controlled by the borrow/return flow only.
            status.disabled = True
            status.help_text = "Currently borrowed. Status changes when it is returned."
        else:
            status.choices = [
                c for c in Asset.Availability.choices if c[0] != Asset.Availability.BORROWED
            ]
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_asset_code(self):
        return self.cleaned_data["asset_code"].strip().upper()