from fastapi import Depends
from typing import Annotated
from hh.user.service import UserService

IUserService: type[UserService] = Annotated[UserService, Depends()]