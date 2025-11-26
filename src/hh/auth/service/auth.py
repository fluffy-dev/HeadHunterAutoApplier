from fastapi.security import OAuth2PasswordRequestForm

from hh.auth.dependencies.user_repository import IUserRepository
from hh.auth.dto import FindUserDTO
from hh.auth.exceptions import UserNotFound
from hh.auth.service.password import PasswordService
from hh.auth.service.token import TokenService
from hh.auth.dto import TokenDTO

class AuthService:
    """
    Service layer for authentication logic.
    """
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def login(self, form_data: OAuth2PasswordRequestForm) -> TokenDTO:
        """
        Authenticates a user and issues JWT tokens.

        Args:
            form_data (OAuth2PasswordRequestForm): The user's login and password.

        Returns:
            TokenDTO: A DTO containing the access and refresh tokens.

        Raises:
            UserNotFound: If the user does not exist or password is incorrect.
        """
        user = await self.user_repo.find(FindUserDTO(login=form_data.username))
        if not user:
            raise UserNotFound

        if not PasswordService.verify_password(form_data.password, user.password):
            raise UserNotFound

        access_token = TokenService.create_access_token(data={"sub": str(user.id)})
        refresh_token = TokenService.create_refresh_token(data={"sub": str(user.id)})

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    #TODO: Add registration endpoint

    async def register(self, form_data) -> TokenDTO:
        ...