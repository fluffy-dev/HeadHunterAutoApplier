from typing import Optional, List

from hh.vacancy.dependencies.repository import IVacancyRepository
from hh.vacancy.dto import SearchSettingsDTO, SearchSettingsUpdateDTO
from hh.vacancy.models import UserHHProfileModel
from hh.integration.hh.dto import HHTokenDTO
from hh.integration.hh.dependencies.service import IHHService
from hh.worker.tasks import process_user_vacancies


class VacancyService:
    """
    Business logic for managing user's HH settings, profile, and bot state.
    """

    def __init__(self, repo: IVacancyRepository, hh_service: IHHService):
        self.repo = repo
        self.hh_service = hh_service

    async def connect_hh_profile(self, user_id: int, code: str) -> None:
        """
        Orchestrates the HH OAuth flow:
        1. Exchanges code for tokens.
        2. Fetches HH user info (to get the real HH ID).
        3. Upserts the profile in the database.

        Args:
            user_id: The application's internal user ID.
            code: The OAuth authorization code.
        """
        # 1. Exchange code
        tokens = await self.hh_service.exchange_code_for_token(code)

        # 2. Get User Info
        me_info = await self.hh_service.get_user_info(tokens.access_token)
        hh_id = int(me_info["id"])

        # 3. Save to DB
        await self.repo.upsert_hh_profile(
            user_id=user_id,
            hh_id=hh_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token
        )

    async def get_settings(self, user_id: int) -> Optional[SearchSettingsDTO]:
        model = await self.repo.get_settings(user_id)
        if not model:
            return None
        return SearchSettingsDTO.model_validate(model)

    async def upsert_settings(self, user_id: int, dto: SearchSettingsUpdateDTO) -> SearchSettingsDTO:
        model = await self.repo.upsert_settings(user_id, dto)
        return SearchSettingsDTO.model_validate(model)

    async def get_hh_profile(self, user_id: int) -> Optional[UserHHProfileModel]:
        return await self.repo.get_hh_profile(user_id)

    async def set_bot_state(self, user_id: int, is_active: bool) -> dict:
        """
        Enables or disables the bot. If enabled, triggers the worker task.
        """
        await self.repo.update_bot_state(user_id, is_active)

        if is_active:
            # Trigger Celery Task
            process_user_vacancies.delay(user_id)
            return {"status": "started"}
        return {"status": "stopped"}

    async def get_resumes(self, user_id: int) -> List[dict]:
        """
        Fetches resumes from HH using the user's stored token.
        """
        profile = await self.repo.get_hh_profile(user_id)
        if not profile or not profile.access_token:
            raise Exception("HH Account not connected")

        return await self.hh_service.get_my_resumes(profile.access_token)

    async def save_hh_tokens(self, user_id: int, tokens: HHTokenDTO, hh_id: int) -> None:
        """
        Saves or updates the HH tokens for a user.

        Args:
            user_id: The internal user ID.
            tokens: The DTO containing access and refresh tokens.
            hh_id: The external HeadHunter user ID.
        """
        await self.repo.upsert_hh_profile(
            user_id=user_id,
            hh_id=hh_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token
        )