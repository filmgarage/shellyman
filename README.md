# Shellyman Add-on (Ingress)

Home Assistant handles discovery; this add-on focuses on **management** (auth on/off, bulk ops, firmware next).

## Install (as local add-on repo)
1. Push this repo to GitHub.
2. In Home Assistant: **Settings → Add-ons → Add-on store → ⋮ → Repositories → Add** your repo URL.
3. Find **Shellyman** in the store, install, and start it.
4. Open via **Ingress** (the add-on UI button).

## Options
- `ha_token` (string, required) — long-lived token for the HA WebSocket API
- `hass_ws_url` (string, optional) — defaults to `ws://supervisor/core/websocket` when running as an add-on
- `gen1_username` (string, optional)
- `gen1_password` (string, optional)
- `gen2_password` (string, optional, user is `admin` by default)
- `request_timeout` (int, seconds; default 5)

> When enabling authentication on devices already integrated into HA, update your HA Shelly integration credentials accordingly.

## Status
- Device list: pulled from HA via WebSocket (config_entries domain `shelly`) and probed
- Protocol detection: **CoIoT** (Gen1) vs **RPC** (Gen2)
- Gen1 auth: **status + enable/disable implemented**
- Gen2 auth: **SetAuth implemented** (Digest realm extraction + ha1); disable also supported
- Firmware column: placeholder (next step is to call the update-check APIs)
