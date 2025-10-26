import requests
from typing import Optional

class HttpClient:
    """Simple wrapper around requests with timeouts and optional auth."""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def get(self, url: str, auth: Optional[requests.auth.AuthBase] = None):
        return requests.get(url, timeout=self.timeout, auth=auth)

    def post(self, url: str, json: dict | None = None, auth: Optional[requests.auth.AuthBase] = None):
        return requests.post(url, json=json, timeout=self.timeout, auth=auth)

    def get_json(self, url: str, auth: Optional[requests.auth.AuthBase] = None) -> tuple[int, dict | None]:
        r = self.get(url, auth=auth)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, None
