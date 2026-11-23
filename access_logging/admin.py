from django.contrib import admin

from .models import LabVisit


@admin.register(LabVisit)
class LabVisitAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "lab_location", "purpose", "status", "check_in_time", "check_out_time", "duration_minutes")
    list_filter = ("status", "purpose", "room__building", "room")
    search_fields = ("user__username", "user__email", "lab_location", "room__name", "room__code_prefix")
    date_hierarchy = "check_in_time"
    readonly_fields = ("check_in_time",)