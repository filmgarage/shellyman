from pydantic import BaseModel
import os
import json

class AddonOptions(BaseModel):
    ha_token: str | None = None
    hass_ws_url: str | None = None
    gen1_username: str | None = None
    gen1_password: str | None = None
    gen2_password: str | None = None
    request_timeout: int = 5

# Supervisor mounts options at /data/options.json
OPTIONS_PATH = "/data/options.json"

def load_options() -> AddonOptions:
    if os.path.exists(OPTIONS_PATH):
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AddonOptions(**data)
    # Fallback to environment variables (useful for local dev)
    return AddonOptions(
        ha_token=os.getenv("HA_TOKEN"),
        hass_ws_url=os.getenv("HASS_WS_URL", "ws://supervisor/core/websocket"),
        gen1_username=os.getenv("GEN1_USERNAME"),
        gen1_password=os.getenv("GEN1_PASSWORD"),
        gen2_password=os.getenv("GEN2_PASSWORD"),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "5")),
    )
