from django.conf import settings
from django.db import models


class Incident(models.Model):
    class Category(models.TextChoices):
        DAMAGE = "DAMAGE", "Damage"
        MALFUNCTION = "MALFUNCTION", "Malfunction"
        LOSS = "LOSS", "Loss / Missing item"
        SAFETY = "SAFETY", "Safety concern"
        MISCONDUCT = "MISCONDUCT", "Misconduct"
        OTHER = "OTHER", "Other"

    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        REPORTED = "REPORTED", "Reported"
        INVESTIGATION = "INVESTIGATION", "Under Investigation"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incidents_reported"
    )
    visit = models.ForeignKey(
        "access_logging.LabVisit", on_delete=models.PROTECT,
        null=True, blank=True, related_name="incidents",
    )
    equipment_log = models.ForeignKey(
        "equipment.EquipmentLog", on_delete=models.PROTECT,
        null=True, blank=True, related_name="incidents",
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REPORTED)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, related_name="incidents_assigned",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["reporter", "status"]),
        ]

    @property
    def reference(self):
        return f"INC-{self.created_at.year}-{self.pk:04d}"

    def __str__(self):
        return f"{self.reference}: {self.title}"


class IncidentAttachment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="incident_evidence/%Y/%m/")
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name


class IncidentStatusHistory(models.Model):
    """Append-only timeline. Never edited or deleted from the UI."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="history")
    from_status = models.CharField(max_length=15, blank=True)
    to_status = models.CharField(max_length=15)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["changed_at", "id"]

    def __str__(self):
        return f"{self.incident_id}: {self.from_status or '-'} -> {self.to_status}"