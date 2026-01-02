from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated

from app.core.dependencies import DbSession, CurrentUser, oauth2_scheme
from app.schemas.auth import Token, TokenRefresh, UserResponse, LoginRequest, UserCreate
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DbSession,
):
    """
    Register a new user with username, email, and password.
    Password will be automatically hashed before storage.
    """
    auth_service = AuthService(db)
    
    # Check if username already exists
    existing_user = await auth_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Create user with hashed password
    user = await auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: DbSession,
):
    """
    Login with username and password using JSON payload.
    Returns access and refresh tokens.
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    
    return auth_service.create_tokens(user)


@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Logout current user by blacklisting the access token.
    """
    auth_service = AuthService(db)
    await auth_service.logout(token)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: DbSession,
):
    """
    Refresh access token using refresh token.
    Returns new access and refresh tokens.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_access_token(token_data.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current authenticated user information.
    """
    return current_user
