from typing import Optional
from sqlalchemy import select, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from hh.config.database.session import ISession
from hh.vacancy.models import SearchSettingsModel, ApplicationModel, UserHHProfileModel
from hh.vacancy.dto import SearchSettingsDTO


class VacancyRepository:
    """
    Repository for managing Vacancy, Application, and Profile data.
    """

    def __init__(self, session: ISession):
        """
        Initialize the repository.

        Args:
            session: Async SQLAlchemy session.
        """
        self.session = session

    async def get_settings(self, user_id: int) -> Optional[SearchSettingsModel]:
        """
        Retrieve search settings for a user.

        Args:
            user_id: The ID of the user.

        Returns:
            The search settings model or None.
        """
        stmt = select(SearchSettingsModel).where(SearchSettingsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_settings(self, user_id: int, dto: SearchSettingsDTO) -> SearchSettingsModel:
        """
        Create or update search settings.

        Args:
            user_id: The ID of the user.
            dto: Data transfer object with settings.

        Returns:
            The updated/created model.
        """
        values = dto.model_dump(exclude_unset=True)
        values["user_id"] = user_id

        stmt = pg_insert(SearchSettingsModel).values(**values).on_conflict_do_update(
            index_elements=[SearchSettingsModel.user_id],
            set_=values
        ).returning(SearchSettingsModel)

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def log_application(self, user_id: int, vacancy_id: str, status: str):
        """
        Log an application attempt.

        Args:
            user_id: The user ID.
            vacancy_id: The external vacancy ID.
            status: Result status (e.g., 'applied', 'error').
        """
        stmt = insert(ApplicationModel).values(
            user_id=user_id, vacancy_id=vacancy_id, status=status
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def is_applied(self, user_id: int, vacancy_id: str) -> bool:
        """
        Check if the user has already applied to this vacancy locally.

        Args:
            user_id: The user ID.
            vacancy_id: The external vacancy ID.

        Returns:
            True if an application record exists.
        """
        stmt = select(ApplicationModel).where(
            ApplicationModel.user_id == user_id,
            ApplicationModel.vacancy_id == vacancy_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_hh_profile(self, user_id: int) -> Optional[UserHHProfileModel]:
        """
        Get the user's HH OAuth profile.

        Args:
            user_id: The internal user ID.

        Returns:
            UserHHProfileModel or None.
        """
        stmt = select(UserHHProfileModel).where(UserHHProfileModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_hh_profile(self, user_id: int, access_token: str, refresh_token: str):
        """
        Create or update the HH profile tokens.

        Args:
            user_id: The internal user ID.
            access_token: New access token.
            refresh_token: New refresh token.
        """
        values = {
            "user_id": user_id,
            "hh_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        stmt = pg_insert(UserHHProfileModel).values(**values).on_conflict_do_update(
            index_elements=[UserHHProfileModel.user_id],
            set_={
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_tokens(self, user_id: int, access_token: str, refresh_token: str):
        """
        Update only the tokens for an existing profile.

        Args:
            user_id: The internal user ID.
            access_token: New access token.
            refresh_token: New refresh token.
        """
        stmt = update(UserHHProfileModel).where(
            UserHHProfileModel.user_id == user_id
        ).values(
            access_token=access_token,
            refresh_token=refresh_token
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_bot_state(self, user_id: int, is_active: bool):
        """
        Enable or disable the bot.

        Args:
            user_id: The internal user ID.
            is_active: The target state.
        """
        stmt = update(UserHHProfileModel).where(UserHHProfileModel.user_id == user_id).values(is_bot_active=is_active)
        await self.session.execute(stmt)
        await self.session.commit()