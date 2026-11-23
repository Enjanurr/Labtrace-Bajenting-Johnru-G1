from django import forms
from django.db import transaction

from authentication.forms import INPUT_CLASSES

from .models import Asset, Condition, EquipmentLog, Room, derive_room_prefix


class BorrowForm(forms.ModelForm):
    class Meta:
        model = EquipmentLog
        fields = ("asset", "pre_condition")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset"].queryset = Asset.objects.filter(
            availability_status=Asset.Availability.AVAILABLE
        ).order_by("asset_code")
        self.fields["asset"].empty_label = "Select equipment..."
        self.fields["pre_condition"].choices = [("", "Select condition...")] + [
            choice
            for choice in Condition.choices
            if choice[0] != Condition.MISSING
        ]
        self.fields["pre_condition"].label = "Condition before borrowing"

        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES


class ReturnForm(forms.ModelForm):
    class Meta:
        model = EquipmentLog
        fields = ("post_condition",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["post_condition"].required = True
        self.fields["post_condition"].choices = [
            ("", "Select condition...")
        ] + list(Condition.choices)
        self.fields["post_condition"].label = "Condition on return"

        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ("room", "name", "availability_status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = Room.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["room"].empty_label = "Select a room..."
        if self.instance.pk:
            self.fields["room"].required = True
            self.fields["room"].help_text = (
                "Changing rooms does not change the asset code."
            )
        status = self.fields["availability_status"]
        if (
            self.instance.pk
            and self.instance.availability_status == Asset.Availability.BORROWED
        ):
            status.disabled = True
            status.help_text = (
                "Currently borrowed. Status changes when it is returned."
            )
        else:
            status.choices = [
                choice
                for choice in Asset.Availability.choices
                if choice[0] != Asset.Availability.BORROWED
            ]
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_room(self):
        room = self.cleaned_data.get("room")
        if not self.instance.pk and room is None:
            raise forms.ValidationError(
                "Select a room to generate the asset code."
            )
        return room

    def save(self, commit=True):
        asset = super().save(commit=False)
        if not asset.pk:
            if asset.room is None:
                raise ValueError("A room is required to create an asset.")

            with transaction.atomic():
                room = Room.objects.select_for_update().get(pk=asset.room_id)
                next_number = room.last_asset_number + 1
                while Asset.objects.filter(
                    asset_code=f"{room.code_prefix}-{next_number:03d}"
                ).exists():
                    next_number += 1
                asset.asset_code = f"{room.code_prefix}-{next_number:03d}"
                room.last_asset_number = next_number
                room.save(update_fields=["last_asset_number"])
                if commit:
                    asset.save()
        elif commit:
            asset.save()
        return asset


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = (
            "name",
            "code_prefix",
            "lab_type",
            "building",
            "capacity",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code_prefix"].required = False
        self.fields["code_prefix"].help_text = (
            "Optional. If blank, a prefix is derived from the room name."
        )
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASSES

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_code_prefix(self):
        prefix = (self.cleaned_data.get("code_prefix") or "").strip().upper()
        if prefix:
            return prefix
        return derive_room_prefix(self.cleaned_data.get("name", ""))

    def clean(self):
        cleaned = super().clean()
        prefix = cleaned.get("code_prefix")
        if prefix:
            duplicate = Room.objects.filter(code_prefix=prefix)
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                self.add_error(
                    "code_prefix",
                    "This room prefix is already in use.",
                )
        return cleaned
