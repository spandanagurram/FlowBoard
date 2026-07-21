"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from apps.comments.urls import comment_urlpatterns
from apps.projects.urls import project_urlpatterns
from apps.tasks.urls import task_urlpatterns
from apps.workspaces.urls import invitation_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/workspaces/', include('apps.workspaces.urls')),
    path('api/invitations/', include(invitation_urlpatterns)),
    path('api/projects/', include(project_urlpatterns)),
    path('api/tasks/', include(task_urlpatterns)),
    path('api/comments/', include(comment_urlpatterns)),
]
