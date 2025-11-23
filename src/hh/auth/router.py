from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from hh.auth.dependencies.service import IAuthService
from hh.user.exceptions import UserNotFound
from hh.security.dto import TokenDTO
from hh.security.dependencies import ICurrentUser


from hh.integration.hh.dependencies.service import IHHService
from hh.vacancy.dependencies.service import IVacancyService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenDTO)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        service: IAuthService
):
    """
    Provides access and refresh tokens for a valid user.
    """
    try:
        tokens = await service.login(form_data)
        return tokens
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/hh/login-url")
async def get_hh_login_url(hh_service: IHHService):
    """Returns the URL to redirect the user to HH."""
    return {"url": hh_service.get_login_url()}


@router.post("/hh/callback")
async def connect_hh_account(
        code: str,
        user: ICurrentUser,
        hh_service: IHHService,
        vacancy_service: IVacancyService
):
    """
    Exchanges the HH code for tokens and links them to the current user.
    """
    try:
        await vacancy_service.connect_hh_profile(user.id, code, hh_service)
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect HH: {str(e)}")