import mimetypes
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Sequence


def send_email(subject: str, body: str, attachments: Sequence[str | Path] = ()) -> None:
    host = os.environ["SMTP_HOST"]
    recipients = [address.strip() for address in os.environ["EMAIL_TO"].split(",") if address.strip()]
    sender = os.getenv("SMTP_FROM") or os.getenv("SMTP_USERNAME")
    if not sender or not recipients:
        raise ValueError("SMTP_FROM or SMTP_USERNAME and at least one EMAIL_TO are required")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    for attachment in attachments:
        attachment_path = Path(attachment)
        content_type, _ = mimetypes.guess_type(attachment_path.name)
        maintype, subtype = (content_type or "application/octet-stream").split("/", 1)
        message.add_attachment(
            attachment_path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=attachment_path.name,
        )

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
    with smtplib.SMTP(host, port, timeout=20) as server:
        if use_tls:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(message)