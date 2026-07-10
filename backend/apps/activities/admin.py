from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "workspace", "actor", "action", "entity_type")
    list_filter = ("action", "entity_type")
    search_fields = ("description",)
    readonly_fields = (
        "id", "workspace", "actor", "action", "description", "entity_type",
        "entity_id", "metadata", "created_at", "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
