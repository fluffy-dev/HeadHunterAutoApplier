import logging
from typing import Any
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from hh.libs.http.exceptions import (
    NetworkError,
    HttpStatusCodeError,
    RateLimitExceeded,
    UnauthorizedError,
)
from hh.libs.http.throttler import AsyncThrottler

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """
    A robust, production-ready asynchronous HTTP client with built-in retries,
    rate limiting, and standardized error handling.

    This client is designed to be used as an async context manager to ensure
    that the underlying HTTP session is properly closed.

    Features:
    - Automatic retries on transient network errors and rate limit responses (429).
    - Exponential backoff strategy for retries.
    - Configurable request throttling to avoid hitting rate limits.
    - Centralized and consistent exception handling for different HTTP errors.
    - Support for default headers and base URL.
    """

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Compatible; HHAutoApplier/1.0)",
        "Accept": "application/json",
    }

    def __init__(
        self,
        base_url: str = "",
        throttler: AsyncThrottler | None = None,
        headers: dict | None = None,
    ):
        """
        Initializes the AsyncHttpClient.

        Args:
            base_url: The base URL to be prepended to all requests.
            throttler: An optional AsyncThrottler instance for rate limiting.
            headers: Optional dictionary of headers to merge with defaults.
        """
        self.base_url = base_url
        self.throttler = throttler or AsyncThrottler()
        self._headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers,
            timeout=self.DEFAULT_TIMEOUT,
        )

    async def __aenter__(self):
        """Enter the async context manager, returning the client instance."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, ensuring the client is closed."""
        await self.close()

    async def close(self):
        """Closes the underlying httpx.AsyncClient session."""
        if not self._client.is_closed:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((NetworkError, RateLimitExceeded)),
        reraise=True,
    )
    async def request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        json_body: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """
        Performs an asynchronous HTTP request with throttling and error handling.

        Args:
            method: The HTTP method (e.g., 'GET', 'POST').
            url: The URL or path for the request.
            params: Optional dictionary of query parameters.
            json_body: Optional dictionary to be sent as the JSON request body.
            headers: Optional dictionary of headers to override client defaults.

        Returns:
            The JSON response from the server, typically a dict or list.

        Raises:
            RateLimitExceeded: On a 429 status code.
            UnauthorizedError: On a 401 status code.
            HttpStatusCodeError: On any other 4xx or 5xx status code.
            NetworkError: On connection errors or other httpx request issues.
        """
        await self.throttler.acquire(self.base_url or "default")

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                headers=headers,
            )

            # Raise specific exceptions for handled status codes
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                logger.warning(
                    f"Rate limit hit for {response.url}. Retrying after {retry_after}s"
                )
                raise RateLimitExceeded(retry_after=retry_after)

            if response.status_code == 401:
                raise UnauthorizedError(401, "Unauthorized", response.text)

            # Raise a generic error for any other unsuccessful status codes
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error for {e.request.url}: {e}")
            raise HttpStatusCodeError(
                status_code=e.response.status_code,
                message=f"HTTP Error: {e.response.reason_phrase}",
                response_body=e.response.text,
            ) from e
        except httpx.RequestError as e:
            # Construct full URL for logging purposes only
            full_url = urljoin(self.base_url, str(e.request.url))
            logger.warning(f"Network error for {full_url}: {e}")
            raise NetworkError(f"Connection failed: {e}") from e

    async def get(self, url: str, params: dict | None = None, **kwargs) -> Any:
        """Convenience method for making a GET request."""
        return await self.request("GET", url, params=params, **kwargs)

    async def post(self, url: str, json_body: dict | None = None, **kwargs) -> Any:
        """Convenience method for making a POST request."""
        return await self.request("POST", url, json_body=json_body, **kwargs)