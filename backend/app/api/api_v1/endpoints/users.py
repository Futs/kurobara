from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core import security

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/2fa/setup", response_model=dict)
def setup_two_factor(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Setup two-factor authentication.
    """
    # Generate a new secret
    secret = security.generate_totp_secret()
    
    # Generate the URI for QR code
    totp_uri = security.get_totp_uri(secret, current_user.email)
    
    # Generate QR code as base64
    qr_code = security.generate_qr_code(totp_uri)
    
    # Return the secret and QR code
    # The secret should be stored only after verification
    return {
        "secret": secret,
        "qr_code": qr_code
    }


@router.post("/2fa/verify", response_model=schemas.User)
def verify_two_factor_setup(
    *,
    db: Session = Depends(deps.get_db),
    secret: str = Body(...),
    code: str = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Verify and enable two-factor authentication.
    """
    # Verify the code
    if not security.verify_totp(secret, code):
        raise HTTPException(
            status_code=400,
            detail="Invalid authentication code"
        )
    
    # Enable 2FA for the user
    user = crud.user.enable_two_factor(db, user_id=current_user.id, secret=secret)
    return user


@router.post("/2fa/disable", response_model=schemas.User)
def disable_two_factor(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Disable two-factor authentication.
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="Two-factor authentication is not enabled"
        )
    
    user = crud.user.disable_two_factor(db, user_id=current_user.id)
    return user


@router.put("/preferences", response_model=schemas.User)
def update_preferences(
    *,
    db: Session = Depends(deps.get_db),
    preferences: schemas.UserPreferences,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update user preferences.
    """
    user = crud.user.update_preferences(
        db, 
        user_id=current_user.id,
        blur_nsfw=preferences.blur_nsfw,
        show_explicit_on_dashboard=preferences.show_explicit_on_dashboard,
        theme=preferences.theme
    )
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user