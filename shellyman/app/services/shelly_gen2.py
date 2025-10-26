import hashlib
import re
from dataclasses import dataclass
from typing import Optional
from ..utils.http import HttpClient
from .typing import AuthStatus

RPC = "/rpc"
REALM_RE = re.compile(r'realm="(?P<realm>[^"]+)"', re.IGNORECASE)

@dataclass
class Gen2AuthConfig:
    user: str = "admin"  # default user on Gen2

class ShellyGen2:
    def __init__(self, client: HttpClient):
        self.http = client
        self.cfg = Gen2AuthConfig()

    def _fetch_realm(self, ip: str) -> Optional[str]:
        """Trigger a 401 to extract Digest realm from WWW-Authenticate header."""
        url = f"http://{ip}{RPC}/Sys.GetStatus"
        r = self.http.post(url, json={"id": 1, "method": "Sys.GetStatus"})
        if r.status_code != 401:
            # Some firmwares respond 200 even without auth for this method; try another protected method
            r = self.http.post(f"http://{ip}{RPC}/Shelly.GetStatus", json={"id": 1, "method": "Shelly.GetStatus"})
        if r.status_code == 401:
            hdr = r.headers.get("WWW-Authenticate", "")
            m = REALM_RE.search(hdr)
            if m:
                return m.group("realm")
        return None

    def _set_auth_attempts(self, ip: str, payloads: list[dict]) -> bool:
        url = f"http://{ip}{RPC}/Shelly.SetAuth"
        for p in payloads:
            r = self.http.post(url, json={"id": 1, "method": "Shelly.SetAuth", "params": p})
            if r.status_code == 200:
                return True
        return False

    def auth_status(self, ip: str) -> AuthStatus:
        # Unauthenticated RPC probe: protected methods should return 401 when auth ON
        url = f"http://{ip}{RPC}/Sys.GetStatus"
        r = self.http.post(url, json={"id": 1, "method": "Sys.GetStatus"})
        if r.status_code == 200:
            return AuthStatus(enabled=False)
        if r.status_code == 401:
            return AuthStatus(enabled=True)
        return AuthStatus(enabled=None, note=f"unexpected status: {r.status_code}")

    def enable_auth(self, ip: str, password: str) -> bool:
        realm = self._fetch_realm(ip) or "shelly"
        user = self.cfg.user
        ha1 = hashlib.sha256(f"{user}:{realm}:{password}".encode("utf-8")).hexdigest()
        # Try common payload shapes across Gen2 firmwares
        attempts = [
            {"enable": True, "user": user, "ha1": ha1},
            {"enable": True, "digest": {"user": user, "ha1": ha1}},
        ]
        ok = self._set_auth_attempts(ip, attempts)
        return ok

    def disable_auth(self, ip: str) -> bool:
        # Try disabling auth; different firmwares accept different shapes
        attempts = [
            {"enable": False},
            {"enable": True, "user": self.cfg.user, "ha1": ""},  # clear creds
        ]
        ok = self._set_auth_attempts(ip, attempts)
        return ok
