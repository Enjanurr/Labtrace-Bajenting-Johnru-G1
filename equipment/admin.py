from django.contrib import admin
from .models import Room

from .models import Asset, EquipmentLog


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("asset_code", "name", "room", "availability_status")
    list_filter = ("availability_status", "room")
    search_fields = ("asset_code", "name", "room__name", "room__code_prefix")


@admin.register(EquipmentLog)
class EquipmentLogAdmin(admin.ModelAdmin):
    list_display = ("asset", "visit", "borrowed_at", "returned_at", "pre_condition", "post_condition")
    list_filter = ("pre_condition", "post_condition")
    search_fields = ("asset__asset_code", "visit__user__username")
    readonly_fields = ("borrowed_at",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "code_prefix", "lab_type", "capacity", "is_active")
    list_filter = ("lab_type", "is_active")
    search_fields = ("name", "code_prefix")
    readonly_fields = ("last_asset_number",)