from datetime import datetime, timezone, timedelta
import secrets
import os
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictError, UnauthorizedError, NotFoundError, ValidationError
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserUpdate

# 🌟 Add Google OAuth Auth libraries
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Env matching settings loading
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: UserRegister) -> User:
        if await self.repo.get_by_email(data.email):
            raise ConflictError("Email already registered")
        if await self.repo.get_by_username(data.username):
            raise ConflictError("Username already taken")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            preferences={},
        )
        return await self.repo.create(user)

    async def login(self, data: UserLogin) -> Any:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")

        payload = {"sub": str(user.id), "email": user.email, "type": "access"}
        
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token({"sub": str(user.id), "email": user.email, "type": "refresh"}),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }

    # 🌟 NEW: Google Auth Integration Service Logic
    async def google_login(self, token: str) -> Any:
        try:
            # 1. Verify Google ID Token integrity:
            id_info = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )

            # 2. Extract key attributes:
            email = id_info.get("email")
            name = id_info.get("name")
            
            if not email:
                raise ValidationError("Email not provided by Google account.")

            # 3. Check if user already exists in DB:
            user = await self.repo.get_by_email(email)
            
            # 4. If user doesn't exist, create auto-registration record:
            if not user:
                # Username duplicate blocks exceptions safety bypass:
                base_username = email.split("@")[0]
                unique_username = base_username
                
                # Check duplicate username just in case:
                counter = 1
                while await self.repo.get_by_username(unique_username):
                    unique_username = f"{base_username}{counter}"
                    counter += 1

                # Generate secure random random password placeholder
                random_temp_password = secrets.token_urlsafe(16)

                user = User(
                    username=unique_username,
                    email=email,
                    password_hash=hash_password(random_temp_password), # Secured default
                    full_name=name or base_username,
                    preferences={},
                    is_active=True
                )
                user = await self.repo.create(user)

            # 5. Check if existing user deactivated:
            if not user.is_active:
                raise UnauthorizedError("Account is inactive")

            # 6. Generate System Standard Bearer tokens:
            payload = {"sub": str(user.id), "email": user.email, "type": "access"}

            return {
                "access_token": create_access_token(payload),
                "refresh_token": create_refresh_token({"sub": str(user.id), "email": user.email, "type": "refresh"}),
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name
                }
            }

        except ValueError as e:
            raise UnauthorizedError(f"Invalid Google ID token signature verification: {str(e)}")

    async def refresh(self, refresh_token: str) -> Any:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user = await self.repo.get_by_id(int(payload["sub"]))
        if not user:
            raise UnauthorizedError("User not found")

        token_payload = {"sub": str(user.id), "email": user.email, "type": "access"}
        
        return {
            "access_token": create_access_token(token_payload),
            "refresh_token": create_refresh_token({"sub": str(user.id), "email": user.email, "type": "refresh"}),
            "token_type": "bearer"
        }

    async def forgot_password(self, email: str) -> str:
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFoundError("User")

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        return token

    async def reset_password(self, token: str, new_password: str) -> None:
        user = await self.repo.get_by_reset_token(token)
        if not user:
            raise ValidationError("Invalid or expired reset token")
            
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        if user.reset_token_expires < current_time:
            raise ValidationError("Reset token has expired")

        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.preferences is not None:
            user.preferences = {**(user.preferences or {}), **data.preferences}
        return user