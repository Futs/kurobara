from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Check if 2FA is enabled for this user
    if user.two_factor_enabled:
        access_token = security.create_access_token(
            user.id, expires_delta=timedelta(minutes=15), two_factor_verified=False
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "requires_two_factor": True
        }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, two_factor_verified=True
        ),
        "token_type": "bearer",
        "requires_two_factor": False
    }


@router.post("/login/verify-2fa", response_model=schemas.Token)
def verify_two_factor(
    *,
    db: Session = Depends(deps.get_db),
    token_in: str = Body(...),
    code_in: str = Body(...)
) -> Any:
    """
    Verify 2FA code and get a full access token
    """
    try:
        payload = security.jwt.decode(
            token_in, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = schemas.TokenPayload(**payload)
    except (security.jwt.JWTError, ValueError):
        raise HTTPException(
            status_code=403,
            detail="Invalid token",
        )
    
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.two_factor_enabled or not user.two_factor_secret:
        raise HTTPException(status_code=400, detail="Two-factor authentication not enabled")
    
    if not security.verify_totp(user.two_factor_secret, code_in):
        raise HTTPException(status_code=400, detail="Invalid authentication code")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, two_factor_verified=True
        ),
        "token_type": "bearer",
        "requires_two_factor": False
    }


@router.post("/login/google", response_model=schemas.Token)
def login_google(
    *,
    db: Session = Depends(deps.get_db),
    oauth_in: schemas.OAuthLogin
) -> Any:
    """
    OAuth login with Google
    """
    # In a real implementation, we would verify the Google OAuth code
    # and get user information from Google
    # For this example, we'll simulate it
    
    # Simulate getting user info from Google
    email = "google_user@example.com"
    oauth_id = "google_123456789"
    full_name = "Google User"
    
    # Check if user exists
    user = crud.user.get_by_oauth(db, provider="google", oauth_id=oauth_id)
    
    # If not, create a new user
    if not user:
        user = crud.user.create_oauth_user(
            db, email=email, provider="google", oauth_id=oauth_id, full_name=full_name
        )
    
    # Check if 2FA is enabled for this user
    if user.two_factor_enabled:
        access_token = security.create_access_token(
            user.id, expires_delta=timedelta(minutes=15), two_factor_verified=False
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "requires_two_factor": True
        }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, two_factor_verified=True
        ),
        "token_type": "bearer",
        "requires_two_factor": False
    }


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    # In a real app, send the email with the token
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}