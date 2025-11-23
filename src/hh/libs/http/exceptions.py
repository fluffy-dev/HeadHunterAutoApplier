class HttpRequestError(Exception):
    """Base class for HTTP errors."""
    pass

class NetworkError(HttpRequestError):
    """Raised on connection timeouts or DNS failures."""
    pass

class HttpStatusCodeError(HttpRequestError):
    """Raised when response status code is 4xx or 5xx."""
    def __init__(self, status_code: int, message: str, response_body: str | None = None):
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        super().__init__(f"HTTP {status_code}: {message}")

class RateLimitExceeded(HttpStatusCodeError):
    """Raised on 429."""
    def __init__(self, retry_after: int = 60, response_body: str | None = None):
        self.retry_after = retry_after
        super().__init__(429, f"Rate limit exceeded. Retry after {retry_after}s", response_body)

class UnauthorizedError(HttpStatusCodeError):
    """Raised on 401."""
    pass