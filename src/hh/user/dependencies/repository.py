from fastapi import Depends
from typing import Annotated
from hh.user.repositories.user import UserRepository

IUserRepository: type[UserRepository] = Annotated[UserRepository, Depends()]