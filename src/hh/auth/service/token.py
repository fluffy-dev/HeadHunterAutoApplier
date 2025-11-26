from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from hh.config.security import settings as auth_settings
from hh.auth.dto import TokenPayloadDTO

class TokenService:
    """
    Provides services for creating and validating JWT tokens.
    """
    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayloadDTO]:
        try:
            payload = jwt.decode(
                token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM]
            )
            return TokenPayloadDTO(**payload)
        except JWTError:
            return None