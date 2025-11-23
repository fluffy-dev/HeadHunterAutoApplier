from urllib.parse import urlencode

from hh.libs.http.client import AsyncHttpClient
from hh.integration.hh.dto import HHSearchResultsDTO, HHNegotiationPayloadDTO, HHTokenDTO
from hh.config.headhunter import settings as hh_settings


class HHIntegrationService:
    """
    Service for interacting with HeadHunter API.
    """
    BASE_URL = "https://api.hh.ru"

    def __init__(self, http_client: AsyncHttpClient | None = None):
        """
        Initializes the HH integration service.

        Args:
            http_client: Optional AsyncHttpClient instance.
        """
        self.client = http_client or AsyncHttpClient(base_url=self.BASE_URL)

    async def close(self):
        """
        Closes the underlying HTTP client.
        """
        await self.client.close()

    def _auth_headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def get_login_url(self) -> str:
        """
        Generates the URL for the frontend to redirect the user to.

        Returns:
            The OAuth authorization URL.
        """
        params = {
            "response_type": "code",
            "client_id": hh_settings.client_id,
            "redirect_uri": hh_settings.redirect_uri,
        }
        return f"{hh_settings.auth_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> HHTokenDTO:
        """
        Exchanges authorization code for access/refresh tokens.

        Args:
            code: The authorization code received from HH.

        Returns:
            DTO containing access and refresh tokens.
        """
        payload = {
            "grant_type": "authorization_code",
            "client_id": hh_settings.client_id,
            "client_secret": hh_settings.client_secret,
            "code": code,
            "redirect_uri": hh_settings.redirect_uri,
        }

        data = await self.client.post(
            hh_settings.token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return HHTokenDTO(**data)

    async def refresh_token(self, refresh_token: str) -> HHTokenDTO:
        """
        Refreshes the access token using the refresh token.

        Args:
            refresh_token: The current refresh token.

        Returns:
            DTO containing new access and refresh tokens.
        """
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": hh_settings.client_id,
            "client_secret": hh_settings.client_secret,
        }

        data = await self.client.post(
            hh_settings.token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return HHTokenDTO(**data)

    async def get_my_resumes(self, token: str) -> list[dict]:
        """
        Fetch user resumes.

        Args:
            token: Valid access token.

        Returns:
            List of resume dictionaries.
        """
        data = await self.client.get("/resumes/mine", headers=self._auth_headers(token))
        return data.get("items", [])

    async def search_vacancies(
            self,
            token: str,
            text: str,
            page: int = 0,
            per_page: int = 20,
            **filters
    ) -> HHSearchResultsDTO:
        """
        Search for vacancies with filters.

        Args:
            token: Valid access token.
            text: Search query string.
            page: Page number (0-indexed).
            per_page: Items per page.
            **filters: Additional query parameters (area, salary, etc).

        Returns:
            Search results DTO.
        """
        params = {
            "text": text,
            "page": page,
            "per_page": per_page,
            **{k: v for k, v in filters.items() if v is not None}
        }

        data = await self.client.get(
            "/vacancies",
            params=params,
            headers=self._auth_headers(token)
        )
        return HHSearchResultsDTO(**data)

    async def apply_for_vacancy(
            self,
            token: str,
            payload: HHNegotiationPayloadDTO
    ) -> bool:
        """
        Apply to a vacancy.

        Args:
            token: Valid access token.
            payload: Negotiation payload containing vacancy_id, resume_id, and message.

        Returns:
            True if application was successful.
        """
        await self.client.post(
            "/negotiations",
            json_body=payload.model_dump(),
            headers=self._auth_headers(token)
        )
        return True

    async def get_user_info(self, token: str) -> dict:
        """
        Fetches the current user's information from HH (GET /me).

        Args:
            token: Valid access token.

        Returns:
            Dictionary containing user info (id, email, etc).
        """
        return await self.client.get("/me", headers=self._auth_headers(token))