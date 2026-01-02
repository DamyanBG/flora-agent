from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token, get_token_expiry_seconds, get_password_hash
from app.schemas.auth import Token, UserCreate
from app.utils.cache import blacklist_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for a user."""
        token_data = {"sub": user.id}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        return Token(access_token=access_token, refresh_token=refresh_token)
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if payload is None:
            return None
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        # Verify user exists and is active
        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            return None
        
        # Create new tokens
        return self.create_tokens(user)
    
    async def logout(self, token: str) -> None:
        """Logout user by blacklisting the token."""
        ttl = get_token_expiry_seconds(token)
        if ttl > 0:
            await blacklist_token(token, ttl)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            user_data: User creation data containing username, email, and plain password
            
        Returns:
            Created user object with hashed password
        """
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user

