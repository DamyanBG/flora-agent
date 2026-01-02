"""
Utility module for password hashing operations.

This module provides convenient functions for hashing and verifying passwords
using the application's password hashing configuration.
"""

from app.core.security import get_password_hash, verify_password


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        plain_password: The plain text password to hash
        
    Returns:
        The hashed password string
        
    Example:
        >>> hashed = hash_password("mySecurePassword123")
        >>> print(hashed)
        $2b$12$...
    """
    return get_password_hash(plain_password)


def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to check against
        
    Returns:
        True if the password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("myPassword")
        >>> check_password("myPassword", hashed)
        True
        >>> check_password("wrongPassword", hashed)
        False
    """
    return verify_password(plain_password, hashed_password)


if __name__ == "__main__":
    # Example usage when running this file directly
    import sys
    
    if len(sys.argv) > 1:
        password = sys.argv[1]
        hashed = hash_password(password)
        print(f"Original password: {password}")
        print(f"Hashed password: {hashed}")
        print(f"\nVerification test: {check_password(password, hashed)}")
    else:
        print("Usage: python -m app.utils.password_hasher <password>")
        print("\nExample:")
        print("  python -m app.utils.password_hasher mySecurePassword123")


