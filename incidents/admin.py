from django.contrib import admin

from .models import Incident, IncidentAttachment, IncidentStatusHistory


class AttachmentInline(admin.TabularInline):
    model = IncidentAttachment
    extra = 0


class HistoryInline(admin.TabularInline):
    model = IncidentStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "changed_by", "note", "changed_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "reporter", "category", "severity", "status", "created_at")
    list_filter = ("status", "severity", "category")
    search_fields = ("title", "reporter__email")
    inlines = [AttachmentInline, HistoryInline]