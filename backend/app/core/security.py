import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import jwt
import pyotp
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, two_factor_verified: bool = False
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "two_factor_verified": two_factor_verified,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_oauth_token(token: str, provider: str) -> Dict[str, Any]:
    """
    Verify an OAuth token with the appropriate provider
    """
    if provider == "google":
        return verify_google_token(token)
    elif provider == "github":
        return verify_github_token(token)
    else:
        raise ValueError(f"Unsupported OAuth provider: {provider}")


def verify_google_token(token: str) -> Dict[str, Any]:
    """
    Verify a Google OAuth token and return user information
    In a production environment, this would make a request to Google's tokeninfo endpoint
    """
    # This is a placeholder - in production, use Google's API client library
    # from google.oauth2 import id_token
    # from google.auth.transport import requests
    # try:
    #     idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
    #     return idinfo
    # except ValueError:
    #     raise HTTPException(status_code=401, detail="Invalid Google token")
    
    # For development/testing, return mock data
    return {
        "sub": "google_123456789",
        "email": "user@example.com",
        "name": "Test User",
        "email_verified": True
    }


def verify_github_token(token: str) -> Dict[str, Any]:
    """
    Verify a GitHub OAuth token and return user information
    In a production environment, this would make a request to GitHub's API
    """
    # This is a placeholder - in production, use GitHub's API
    # import requests
    # headers = {"Authorization": f"token {token}"}
    # response = requests.get("https://api.github.com/user", headers=headers)
    # if response.status_code != 200:
    #     raise HTTPException(status_code=401, detail="Invalid GitHub token")
    # return response.json()
    
    # For development/testing, return mock data
    return {
        "id": "github_123456789",
        "email": "user@example.com",
        "name": "Test User",
        "login": "testuser"
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_totp_secret() -> str:
    """Generate a new TOTP secret for 2FA"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Generate a TOTP URI for QR code generation"""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email, issuer_name=settings.PROJECT_NAME
    )


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against a secret"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_qr_code(totp_uri: str) -> str:
    """Generate a QR code image as a base64 string with optimized settings"""
    # Use a more efficient QR version and adjust parameters
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Better error correction
        box_size=8,  # Smaller box size still readable but faster
        border=2,    # Smaller border still valid
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 with improved buffer handling
    with io.BytesIO() as buffer:
        img.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
