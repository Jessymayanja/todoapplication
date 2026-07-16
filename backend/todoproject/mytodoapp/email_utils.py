from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import striptags
import logging

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Shared email utility used by both verification emails and
    deadline reminders. Uses Django's built-in send_mail which
    reads SMTP settings from settings.py automatically.

    Returns True if the email was accepted, False on any failure,
    so calling code can decide whether to retry rather than crashing.
    """
    try:
        text_content = striptags(html_content)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        message.attach_alternative(html_content, "text/html")
        message.send(fail_silently=False)
        logger.info("Email sent to %s subject=%r", to_email, subject)
        return True
    except Exception as exc:
        logger.exception("Email failed to %s subject=%r", to_email, subject)
        return False