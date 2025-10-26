from requests.auth import HTTPBasicAuth
from .typing import AuthStatus
from ..utils.http import HttpClient

STATUS_PATH = "/status"
LOGIN_PATH = "/settings/login"

class ShellyGen1:
    def __init__(self, client: HttpClient):
        self.http = client

    def auth_status(self, ip: str) -> AuthStatus:
        # Unauthenticated probe: 200 => auth OFF, 401 => auth ON
        status_code, _ = self.http.get_json(f"http://{ip}{STATUS_PATH}")
        if status_code == 200:
            return AuthStatus(enabled=False)
        if status_code == 401:
            return AuthStatus(enabled=True)
        return AuthStatus(enabled=None, note=f"unexpected status: {status_code}")

    def enable_auth(self, ip: str, username: str, password: str) -> bool:
        # Enable login; after enabling, most endpoints require Basic auth
        url = f"http://{ip}{LOGIN_PATH}?enabled=1&username={username}&password={password}"
        r = self.http.post(url)
        return r.status_code in (200, 204)

    def disable_auth(self, ip: str, username: str | None = None, password: str | None = None) -> bool:
        # If auth is already enabled, call with BasicAuth; otherwise open call also works
        url = f"http://{ip}{LOGIN_PATH}?enabled=0"
        auth = HTTPBasicAuth(username, password) if username and password else None
        r = self.http.post(url, auth=auth)
        return r.status_code in (200, 204)
