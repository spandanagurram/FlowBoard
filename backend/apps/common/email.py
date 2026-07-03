from collections.abc import Mapping, Sequence

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

def send_email(
    *,
    subject: str,
    message: str,
    recipients: Sequence[str],
) -> int:
    """
    Send a plain text email.
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
    
    
def send_templated_email(
    *,
    subject: str,
    template_name: str,
    context: Mapping[str, object],
    recipients: Sequence[str],
) -> int:
    """
    Render a Django template and send it as an HTML email.

    Returns:
        int: Number of successfully delivered messages.
    """
    html_content = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body="Please use an HTML-compatible email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(recipients),
    )

    email.attach_alternative(html_content, "text/html")

    return email.send()