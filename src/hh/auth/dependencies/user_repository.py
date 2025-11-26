from fastapi import Depends
from typing import Annotated
from hh.auth.repositories.user import UserRepository

IUserRepository: type[UserRepository] = Annotated[UserRepository, Depends()]