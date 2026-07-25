from django.conf import settings

from apps.workspaces.tasks import send_workspace_invitation_email


def dispatch_workspace_invitation_email(invitation_id):
    """
    Sends invitation email asynchronously using Celery
    or synchronously based on configuration.
    """

    if settings.USE_CELERY:
        send_workspace_invitation_email.delay(str(invitation_id))
    else:
        send_workspace_invitation_email(str(invitation_id))