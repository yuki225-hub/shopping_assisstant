from datetime import datetime, timedelta
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictError, UnauthorizedError, NotFoundError, ValidationError
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserUpdate


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

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")

        payload = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
            user=user,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user = await self.repo.get_by_id(int(payload["sub"]))
        if not user:
            raise UnauthorizedError("User not found")

        token_payload = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(token_payload),
            refresh_token=create_refresh_token(token_payload),
        )

    async def forgot_password(self, email: str) -> str:
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFoundError("User")

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return token  # In production: send via email

    async def reset_password(self, token: str, new_password: str) -> None:
        user = await self.repo.get_by_reset_token(token)
        if not user:
            raise ValidationError("Invalid or expired reset token")
        if user.reset_token_expires < datetime.utcnow():
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
