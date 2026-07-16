import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

logger = logging.getLogger(__name__)

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.BREVO_API_KEY

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": settings.DEFAULT_FROM_EMAIL},
        subject=subject,
        html_content=html_content,
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
        logger.info("Email sent to %s subject=%r", to_email, subject)
        return True
    except ApiException as exc:
        logger.exception("Email failed to %s subject=%r", to_email, subject)
        return False