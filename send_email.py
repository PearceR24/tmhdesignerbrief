import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


def send_designer_brief(pdf_bytes: bytes, client_names: str, site_address: str):
    sender = os.environ["OUTLOOK_EMAIL"]
    password = os.environ["OUTLOOK_PASSWORD"]
    recipient = os.environ["DESIGNER_EMAIL"]

    # Derive a clean filename from the address
    safe_address = site_address.replace(",", "").replace("  ", " ").strip()
    filename = f"Designer Brief - {safe_address}.pdf"

    # Short, professional email body
    body = f"""Hi Matthew,

Please find attached a new Designer Briefing Document for {client_names} at {site_address}.

This brief has been automatically generated from Pearce's post-meeting notes. Please review and proceed with the site assessment as outlined.

Any questions, don't hesitate to reach out.

Cheers,
Pearce
Tasman Manufactured Housing
admin@tasmanufacturedhousing.com.au"""

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = f"New Designer Brief – {site_address}"
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Email sent to {recipient} — {filename}")
