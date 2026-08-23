import time
from typing import Any, Dict, Generator, Optional

import httpx


class AdapterError(Exception):
    """Base exception for adapter-related errors."""

    pass


class AuthError(AdapterError):
    """Raised when authentication fails (e.g., 401, 403)."""

    pass


class NetworkError(AdapterError):
    """Raised when a network error or timeout occurs."""

    pass


class MalformedResponseError(AdapterError):
    """Raised when the response is not in the expected format (e.g., invalid JSON)."""

    pass


class HTTPClient:
    def __init__(
        self, timeout: float = 30.0, max_retries: int = 3, retry_delay: float = 1.0
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        if response.status_code in (401, 403):
            raise AuthError(
                f"Authentication failed: {response.status_code} {response.text}"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise AdapterError(
                f"HTTP error occurred: {e.response.status_code} {e.response.text}"
            ) from e
        return response

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exception = None

        # Ensure timeout is set
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        for attempt in range(self.max_retries):
            try:
                with httpx.Client() as client:
                    response = client.request(method, url, **kwargs)
                    return self._handle_response(response)
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(
                        f"Network error after {self.max_retries} attempts: {str(e)}"
                    ) from e

        raise NetworkError(f"Request failed: {str(last_exception)}")

    def get(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> httpx.Response:
        return self._request("GET", url, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> httpx.Response:
        return self._request("POST", url, headers=headers, json=json, **kwargs)

    def stream_post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        # Generator for streaming response using iter_lines()
        last_exception = None

        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        for attempt in range(self.max_retries):
            try:
                with httpx.Client() as client:
                    with client.stream(
                        "POST", url, headers=headers, json=json_payload, **kwargs
                    ) as response:
                        if response.status_code in (401, 403):
                            response.read()
                            raise AuthError(
                                f"Authentication failed: {response.status_code} {response.text}"
                            )
                        try:
                            response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            response.read()
                            raise AdapterError(
                                f"HTTP error occurred: {e.response.status_code} {e.response.text}"
                            ) from e

                        for line in response.iter_lines():
                            yield line
                return
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(
                        f"Network error after {self.max_retries} attempts: {str(e)}"
                    ) from e

        raise NetworkError(f"Stream request failed: {str(last_exception)}")
