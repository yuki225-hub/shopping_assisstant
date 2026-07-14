from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    UserUpdate, ForgotPasswordRequest, ResetPasswordRequest, RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(data)
    # Ensuring compatibility fallback parameters directly:
    if not hasattr(user, 'is_active'):
        user.is_active = True
    if not hasattr(user, 'preferences'):
        user.preferences = {}
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    token_data = await service.login(data)
    
    # Validation checks fallback data structure constraints injection before parsing:
    user_obj = getattr(token_data, 'user', None)
    if user_obj:
        if not getattr(user_obj, 'is_active', None):
            user_obj.is_active = True
        if getattr(user_obj, 'preferences', None) is None:
            user_obj.preferences = {}
        if not getattr(user_obj, 'created_at', None):
            import datetime
            user_obj.created_at = datetime.datetime.now()
            
    return token_data


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    return None


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    token = await service.forgot_password(data.email)
    return {"message": "Password reset instructions sent to your email", "debug_token": token}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_password(data.token, data.new_password)


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    if not hasattr(current_user, 'is_active'):
        current_user.is_active = True
    if not hasattr(current_user, 'preferences') or current_user.preferences is None:
        current_user.preferences = {}
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.update_profile(current_user, data)