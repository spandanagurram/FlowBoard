from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from apps.common.email import send_templated_email
from apps.workspaces.models import WorkspaceInvitation
from config import settings


@shared_task
def send_workspace_invitation_email(invitation_id: str) -> None:
    try:
        invitation = (
            WorkspaceInvitation.objects
            .select_related("workspace", "invited_by")
            .get(id=invitation_id, workspace__is_deleted=False)
        )
    except WorkspaceInvitation.DoesNotExist:
        # We'll replace this with proper logging later.
        print(f"Invitation {invitation_id} not found.")
        return

    inviter_name = (
        invitation.invited_by.get_full_name()
        or invitation.invited_by.username
    )

    subject = f"Invitation to join {invitation.workspace.name}"
    invitation_url = (
    f"{settings.FRONTEND_URL}/invitations/{invitation.token}"
    )

    send_templated_email(
    subject=subject,
    template_name="emails/workspace_invitation.html",
    context={
        "inviter_name": inviter_name,
        "workspace_name": invitation.workspace.name,
        "invitation_url": invitation_url,
    },
    recipients=[invitation.email],
   )

    
@shared_task
def expire_pending_invitations():
    from .services import InvitationService
    """
    Expire all pending invitations that have passed their expiry time.
    """
    return InvitationService.expire_pending_invitations()
