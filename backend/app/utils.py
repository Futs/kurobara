import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

import emails
from emails.template import JinjaTemplate
from jose import jwt

from app.core.config import settings


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> bool:
    """Send email to specified address with templated content.
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not settings.EMAILS_ENABLED:
        logging.warning("Email functionality disabled in settings")
        return False
    
    try:
        message = emails.Message(
            subject=JinjaTemplate(subject_template),
            html=JinjaTemplate(html_template),
            mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        )
        
        smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        if settings.SMTP_TLS:
            smtp_options["tls"] = True
        if settings.SMTP_USER:
            smtp_options["user"] = settings.SMTP_USER
        if settings.SMTP_PASSWORD:
            smtp_options["password"] = settings.SMTP_PASSWORD
            
        response = message.send(to=email_to, render=environment, smtp=smtp_options)
        logging.info(f"Send email result: {response}")
        return response.status_code in (250, 200, 201, 202)
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False


@lru_cache(maxsize=8)
def _load_email_template(template_name: str) -> str:
    """Load and cache email template content."""
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / template_name
    try:
        with open(template_path) as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Email template not found: {template_path}")
        return "<p>Email template missing</p>"


def send_test_email(email_to: str) -> bool:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    template_str = _load_email_template("test_email.html")
    return send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": project_name, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> bool:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    template_str = _load_email_template("reset_password.html")
    link = f"{settings.SERVER_HOST}/reset-password?token={token}"
    return send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> bool:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    template_str = _load_email_template("new_account.html")
    return send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.SERVER_HOST,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    payload = {"exp": expires.timestamp(), "nbf": now.timestamp(), "sub": email}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError as e:
        logging.warning(f"Invalid password reset token: {str(e)}")
        return None