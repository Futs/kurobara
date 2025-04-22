from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext
import pyotp
import qrcode
import io
import base64

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, two_factor_verified: bool = False
) -> str:
    # Use the imported timezone directly instead of reimporting
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "two_factor_verified": two_factor_verified,
        "iat": datetime.now(timezone.utc)  # Add issued-at time for better security
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_totp_secret() -> str:
    """Generate a new TOTP secret for 2FA"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Get the TOTP URI for QR code generation"""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email, issuer_name=settings.PROJECT_NAME
    )


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against a secret using time-safe comparison"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


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