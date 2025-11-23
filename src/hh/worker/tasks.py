import asyncio
import logging
import json
from celery import Task

from hh.config.celery import celery_app
from hh.config.database.engine import db_helper
from hh.integration.hh.service import HHIntegrationService
from hh.integration.hh.dto import HHNegotiationPayloadDTO, HHTokenDTO
from hh.vacancy.repository.vacancy import VacancyRepository
from hh.libs.http.client import AsyncHttpClient
from hh.libs.http.exceptions import UnauthorizedError, HttpStatusCodeError

logger = logging.getLogger(__name__)


class AutoApplyTask(Task):
    """
    Base Celery task with retry configuration.
    """
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}


async def _refresh_access_token(
        hh_service: HHIntegrationService,
        repo: VacancyRepository,
        user_id: int,
        refresh_token: str
) -> HHTokenDTO:
    """
    Refreshes the HH tokens and updates the database.

    Args:
        hh_service: Service to communicate with HH.
        repo: Repository to update DB.
        user_id: ID of the user owner.
        refresh_token: The expired refresh token.

    Returns:
        The new token DTO.

    Raises:
        UnauthorizedError: If the refresh token is also invalid.
    """
    new_tokens = await hh_service.refresh_token(refresh_token)
    await repo.update_tokens(user_id, new_tokens.access_token, new_tokens.refresh_token)
    logger.info(f"Tokens refreshed for user {user_id}")
    return new_tokens


async def _process_user_async(user_id: int):
    """
    Main asynchronous logic for processing a user's vacancy applications.

    Iterates through search pages and applies to vacancies. Handles pagination,
    token refreshing on 401 errors, and graceful skipping of duplicate applications.

    Args:
        user_id: The ID of the user to process.
    """
    http_client = AsyncHttpClient()
    hh_service = HHIntegrationService(http_client=http_client)

    async with db_helper.session_factory() as session:
        repo = VacancyRepository(session)

        hh_profile = await repo.get_hh_profile(user_id)
        settings = await repo.get_settings(user_id)

        if not hh_profile or not hh_profile.is_bot_active or not settings:
            logger.info(f"Bot inactive or no settings for user {user_id}")
            await hh_service.close()
            return

        current_token = hh_profile.access_token
        current_refresh_token = hh_profile.refresh_token

        page = 0
        while True:
            try:
                search_res = await hh_service.search_vacancies(
                    token=current_token,
                    text=settings.search_text,
                    area=settings.area_id,
                    salary=settings.salary,
                    page=page
                )
            except UnauthorizedError:
                try:
                    tokens = await _refresh_access_token(hh_service, repo, user_id, current_refresh_token)
                    current_token = tokens.access_token
                    current_refresh_token = tokens.refresh_token
                    continue
                except Exception as e:
                    logger.error(f"Failed to refresh token for user {user_id}: {e}")
                    break
            except Exception as e:
                logger.error(f"Search failed for user {user_id} on page {page}: {e}")
                break

            if not search_res.items:
                break

            for item in search_res.items:
                if await repo.is_applied(user_id, item.id):
                    continue

                try:
                    payload = HHNegotiationPayloadDTO(
                        vacancy_id=item.id,
                        resume_id=settings.resume_id,
                        message=settings.cover_letter or ""
                    )
                    await hh_service.apply_for_vacancy(current_token, payload)
                    await repo.log_application(user_id, item.id, "applied")
                    logger.info(f"Applied to vacancy {item.id} for user {user_id}")

                    await asyncio.sleep(2)

                except UnauthorizedError:
                    try:
                        tokens = await _refresh_access_token(hh_service, repo, user_id, current_refresh_token)
                        current_token = tokens.access_token
                        current_refresh_token = tokens.refresh_token

                        await hh_service.apply_for_vacancy(current_token, payload)
                        await repo.log_application(user_id, item.id, "applied")

                    except Exception as e:
                        logger.error(f"Retry application failed after refresh for {item.id}: {e}")

                except HttpStatusCodeError as e:
                    error_type = "error"
                    if e.status_code == 403:
                        try:
                            # Attempt to parse HH error body to check for duplicate
                            body_json = json.loads(e.response_body or "{}")
                            errors = body_json.get("errors", [])
                            for err in errors:
                                if err.get("value") == "already_applied":
                                    error_type = "already_applied_external"
                                    break
                        except json.JSONDecodeError:
                            pass

                    if error_type == "already_applied_external":
                        await repo.log_application(user_id, item.id, error_type)
                    else:
                        logger.error(f"HTTP Error applying to {item.id}: {e}")

                except Exception as e:
                    logger.error(f"Unexpected error applying to {item.id}: {e}")

            page += 1
            if page >= search_res.pages:
                break

            await asyncio.sleep(1)

    await hh_service.close()


@celery_app.task(base=AutoApplyTask, bind=True)
def process_user_vacancies(self, user_id: int):
    """
    Celery task entry point to process vacancies for a specific user.

    Args:
        user_id: The ID of the user.
    """
    asyncio.run(_process_user_async(user_id))