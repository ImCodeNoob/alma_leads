import logging
import smtplib
import time
from email.message import EmailMessage
from pathlib import Path

from app.config import settings

logger = logging.getLogger("email_service")


def send_email(to: str, subject: str, body: str, category: str = "general") -> None:
    """Send an email via SMTP if configured, otherwise log it to a file
    (and stdout) so the app is fully usable with zero external config.

    `category` (e.g. "prospect_confirmation", "attorney_notification") is
    purely local bookkeeping for the fallback log — it's never part of the
    actual email sent to a real recipient over SMTP.
    """
    if settings.smtp_host:
        _send_via_smtp(to, subject, body)
    else:
        _log_fallback(to, subject, body, category)


def _send_via_smtp(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


def _log_fallback(to: str, subject: str, body: str, category: str) -> None:
    logger.info(
        "SMTP not configured; logging email instead. category=%s to=%s subject=%s",
        category,
        to,
        subject,
    )

    out_dir = Path(settings.fallback_email_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{int(time.time() * 1000)}_{category}_{to.replace('@', '_at_')}.txt"
    (out_dir / filename).write_text(
        f"Category: {category}\nTo: {to}\nSubject: {subject}\n\n{body}\n"
    )
