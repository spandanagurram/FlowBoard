from apps.projects.models import Project
from apps.tasks.models import Task
from apps.workspaces.models import Workspace
from apps.common.cache import get_cache, set_cache
from django.conf import settings

DASHBOARD_CACHE_TIMEOUT = 300


class DashboardService:
    @staticmethod
    def get_dashboard_summary(user):
        cache_key = f"dashboard_summary_{user.id}"

        cached_summary = get_cache(cache_key)
        if cached_summary:
            print("CACHE HIT")
            return cached_summary
        
        print("CACHE MISS")
        
        workspace_filter = {
            "members__user": user,
            "members__is_active": True,
            "is_deleted": False,
        }

        summary = {
            "workspace_count": Workspace.objects.filter(
                **workspace_filter
            ).distinct().count(),
            "project_count": Project.objects.filter(
                workspace__members__user=user,
                workspace__members__is_active=True,
                workspace__is_deleted=False,
                is_deleted=False,
            ).distinct().count(),
            "task_count": Task.objects.filter(
                project__workspace__members__user=user,
                project__workspace__members__is_active=True,
                project__workspace__is_deleted=False,
                project__is_deleted=False,
                is_deleted=False,
            ).distinct().count(),
        }

        set_cache(cache_key, summary, settings.DASHBOARD_CACHE_TIMEOUT)

        return summary