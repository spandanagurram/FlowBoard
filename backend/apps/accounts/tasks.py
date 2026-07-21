from celery import shared_task

from apps.common.email import send_templated_email


@shared_task
def send_password_reset_email(email: str, reset_url: str) -> None:
    send_templated_email(
        subject="Reset your FlowBoard password",
        template_name="emails/password_reset.html",
        context={"reset_url": reset_url},
        recipients=[email],
    )
