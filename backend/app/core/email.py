import smtplib
from email.message import EmailMessage

from app.core.config import settings

from app.core.config import settings


def render_email(title: str, body_html: str, cta_text: str | None = None, cta_link: str | None = None) -> str:
    """Wraps email content in a branded template -- consistent header band,
    readable body, and a button-style CTA link, matching how GitHub/Slack
    style their transactional emails."""
    cta_block = ""
    if cta_text and cta_link:
        cta_block = f"""
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin:24px 0;">
          <tr>
            <td style="background-color:#534AB7; border-radius:8px;">
              <a href="{cta_link}" style="display:inline-block; padding:12px 28px; color:#ffffff; font-weight:600; font-size:14px; text-decoration:none;">{cta_text}</a>
            </td>
          </tr>
        </table>
        <p style="font-size:12px; color:#8A8580; word-break:break-all;">Or copy this link: <a href="{cta_link}" style="color:#534AB7;">{cta_link}</a></p>
        """

    return f"""
    <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif; max-width:520px; margin:0 auto; border:1px solid #E7E4DD; border-radius:12px; overflow:hidden;">
      <div style="background:linear-gradient(135deg,#6D5DF4,#4338CA); padding:24px 28px;">
        <span style="color:#ffffff; font-size:18px; font-weight:800;">SCNA</span>
        <p style="color:#ffffff; opacity:0.9; font-size:13px; margin:2px 0 0;">Scientific Collaboration Network Analyzer</p>
      </div>
      <div style="padding:28px; color:#1F1D1A;">
        <h2 style="font-size:18px; margin:0 0 12px;">{title}</h2>
        <div style="font-size:14px; line-height:1.6; color:#3D3A35;">{body_html}</div>
        {cta_block}
      </div>
      <div style="padding:16px 28px; background:#FAF9F6; border-top:1px solid #E7E4DD;">
        <p style="font-size:11px; color:#8A8580; margin:0;">If you didn't expect this email, you can safely ignore it.</p>
      </div>
    </div>
    """

def send_email(to_email: str, subject: str, html_body: str) -> None:
    """Sends an email via SMTP. If SMTP isn't configured yet (no username/
    password in .env), falls back to printing the email to the backend
    console instead of raising -- so register/login/forgot-password keep
    working in local dev even before real SMTP credentials are set up."""

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("=" * 60)
        print(f"[DEV EMAIL - SMTP NOT CONFIGURED] To: {to_email}")
        print(f"Subject: {subject}")
        print(html_body)
        print("=" * 60)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.set_content("This email requires an HTML-capable email client.")
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)