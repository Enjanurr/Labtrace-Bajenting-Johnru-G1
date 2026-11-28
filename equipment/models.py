from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, RegexValidator
import re


def derive_room_prefix(name: str) -> str:
    """Convert a room name to a compact prefix, for example 'Computer Lab 1' -> 'CL1'."""
    parts = re.findall(r"[A-Za-z]+|\d+", name or "")
    return "".join(part if part.isdigit() else part[0] for part in parts).upper()[:8]


class Room(models.Model):
    class LabType(models.TextChoices):
        COMPUTER = "COMPUTER", "Computer Lab"
        ELECTRONICS = "ELECTRONICS", "Electronics Lab"
        GENERAL = "GENERAL", "General Lab"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=100, unique=True)
    code_prefix = models.CharField(
        max_length=8,
        unique=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^[A-Z0-9]{2,8}$",
                "Use 2-8 uppercase letters or digits.",
            )
        ],
    )
    lab_type = models.CharField(
        max_length=20,
        choices=LabType.choices,
        default=LabType.GENERAL,
    )
    building = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1)],
    )
    is_active = models.BooleanField(default=True)
    last_asset_number = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code_prefix})"

    def save(self, *args, **kwargs):
        prefix = (self.code_prefix or derive_room_prefix(self.name)).upper()
        if prefix:
            self.code_prefix = prefix
        super().save(*args, **kwargs)


CONDITION_CHOICES = (
    ("GOOD", "Good"),
    ("DAMAGED", "Damaged"),
    ("MALFUNCTIONING", "Malfunctioning"),
    ("MISSING", "Missing"),
)


class Condition(models.TextChoices):
    GOOD = "GOOD", "Good"
    DAMAGED = "DAMAGED", "Damaged"
    MALFUNCTIONING = "MALFUNCTIONING", "Malfunctioning"
    MISSING = "MISSING", "Missing"


class Asset(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BORROWED = "BORROWED", "Borrowed"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        MISSING = "MISSING", "Missing"

    asset_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="assets",
        null=True,
        blank=True,
    )
    availability_status = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
        db_index=True,
    )

    class Meta:
        ordering = ["asset_code"]

    def save(self, *args, **kwargs):
        if not self.pk and not self.asset_code:
            from django.db import transaction

            with transaction.atomic():
                if self.room_id:
                    room = Room.objects.select_for_update().get(pk=self.room_id)
                    next_number = room.last_asset_number + 1
                    while Asset.objects.filter(
                        asset_code=f"{room.code_prefix}-{next_number:03d}"
                    ).exists():
                        next_number += 1
                    self.asset_code = f"{room.code_prefix}-{next_number:03d}"
                    room.last_asset_number = next_number
                    room.save(update_fields=["last_asset_number"])
                else:
                    next_number = 1
                    while Asset.objects.filter(
                        asset_code=f"EQ-{next_number:03d}"
                    ).exists():
                        next_number += 1
                    self.asset_code = f"EQ-{next_number:03d}"
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.asset_code} - {self.name}"


class EquipmentLog(models.Model):
    # PROTECT: history must survive. Soft-delete users/assets instead.
    visit = models.ForeignKey(
        "access_logging.LabVisit",
        on_delete=models.PROTECT,
        related_name="equipment_logs",
    )
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="logs")
    borrowed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    pre_condition = models.CharField(max_length=20, choices=Condition.choices)
    post_condition = models.CharField(
        max_length=20, choices=Condition.choices, null=True, blank=True
    )

    class Meta:
        ordering = ["-borrowed_at"]
        constraints = [
            # An asset can have at most one open (unreturned) log.
            models.UniqueConstraint(
                fields=["asset"],
                condition=Q(returned_at__isnull=True),
                name="one_open_log_per_asset",
            ),
        ]

    @property
    def is_open(self):
        return self.returned_at is None

    def __str__(self):
        return f"{self.asset.asset_code} / {self.visit.user.username}"