from typing import Any, Dict, Optional, Union, TypeVar, Generic

from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_oauth(self, db: Session, *, provider: str, oauth_id: str) -> Optional[User]:
        """Get a user by OAuth provider and ID"""
        return db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id
        ).first()
    
    def _set_default_user_preferences(self, user_obj: User, 
                                     blur_nsfw: Optional[bool] = None,
                                     show_explicit_on_dashboard: Optional[bool] = None, 
                                     theme: Optional[str] = None) -> None:
        """Set default user preferences if not provided"""
        user_obj.blur_nsfw = blur_nsfw if blur_nsfw is not None else True
        user_obj.show_explicit_on_dashboard = show_explicit_on_dashboard if show_explicit_on_dashboard is not None else False
        user_obj.theme = theme if theme is not None else "dark"

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            oauth_provider="email"
        )
        self._set_default_user_preferences(
            db_obj, 
            obj_in.blur_nsfw, 
            obj_in.show_explicit_on_dashboard, 
            obj_in.theme
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_oauth_user(
        self, db: Session, *, email: str, provider: str, oauth_id: str, full_name: str = ""
    ) -> User:
        """Create a new user from OAuth login"""
        db_obj = User(
            email=email,
            full_name=full_name,
            oauth_provider=provider,
            oauth_id=oauth_id,
            is_active=True,
            is_superuser=False,
            two_factor_enabled=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        if "password" in update_data:
            hashed_password = get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def _update_two_factor(self, db: Session, user_id: Any, secret: Optional[str], enabled: bool) -> User:
        """Common method for enabling/disabling two-factor authentication"""
        user = self.get(db, id=user_id)
        user.two_factor_secret = secret
        user.two_factor_enabled = enabled
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def enable_two_factor(self, db: Session, *, user_id: UUID, secret: str) -> User:
        """Enable 2FA for a user"""
        user = self.get(db, id=user_id)
        if not user:
            raise ValueError("User not found")
        
        user.two_factor_secret = secret
        user.two_factor_enabled = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def disable_two_factor(self, db: Session, *, user_id: UUID) -> User:
        """Disable 2FA for a user"""
        user = self.get(db, id=user_id)
        if not user:
            raise ValueError("User not found")
        
        user.two_factor_secret = None
        user.two_factor_enabled = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_preferences(
        self, db: Session, *, user_id: Any, blur_nsfw: Optional[bool] = None, 
        show_explicit_on_dashboard: Optional[bool] = None, theme: Optional[str] = None
    ) -> User:
        user = self.get(db, id=user_id)
        
        # Only update fields that were provided
        if blur_nsfw is not None:
            user.blur_nsfw = blur_nsfw
        if show_explicit_on_dashboard is not None:
            user.show_explicit_on_dashboard = show_explicit_on_dashboard
        if theme is not None:
            user.theme = theme
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user = CRUDUser(User)
