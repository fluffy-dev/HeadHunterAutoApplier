from fastapi import Depends
from typing import Annotated

from hh.auth.service.auth import AuthService

IAuthService: type[AuthService] = Annotated[AuthService, Depends()]