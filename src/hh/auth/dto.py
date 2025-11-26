from pydantic import BaseModel


#Token
class TokenDTO(BaseModel):
    """
    DTO for representing JWT access and refresh tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayloadDTO(BaseModel):
    """
    DTO for the payload data encoded within the JWT.
    'sub' (subject) will typically be the user's ID.
    """
    sub: str | None = None


#User

from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, StringConstraints

class UserDTO(BaseModel):
    """
    Data Transfer Object for a user, including sensitive information like a password.
    Password is optional, typically for creation or updates.
    """
    id: Optional[int] = None
    name: Annotated[str, StringConstraints(max_length=30)]
    login: Annotated[str, StringConstraints(max_length=50)]
    email: EmailStr
    password: Optional[str] = None

class PublicUserDTO(BaseModel):
    """
    A view of a user's data that is safe to be exposed publicly.
    """
    name: Annotated[str, StringConstraints(max_length=30)]

class PrivateUserDTO(BaseModel):
    """
    A private view of a user's data, excluding sensitive details like the password.
    """
    name: Annotated[str, StringConstraints(max_length=30)]
    login: Annotated[str, StringConstraints(max_length=50)]
    email: EmailStr

class FindUserDTO(BaseModel):
    """
    DTO for searching or finding a user by various optional criteria.
    """
    id: Optional[int] = None
    login: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[EmailStr] = None

class UpdateUserDTO(BaseModel):
    """
    DTO for updating a user's information. All fields are optional.
    """
    name: Optional[Annotated[str, StringConstraints(max_length=30)]] = None
    login: Optional[Annotated[str, StringConstraints(max_length=50)]] = None