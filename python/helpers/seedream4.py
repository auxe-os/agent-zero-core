"""Helpers and constants for the Seedream 4.x image generation API.

This module centralises Seedream-specific configuration so tools can
share it without duplicating literals in multiple places.
"""

from __future__ import annotations

from typing import Any, Dict

from python.helpers import dotenv

SEEDREAM4_ENDPOINT = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"


def get_model_name() -> str:
    """Return the Seedream model name, env-overridable.

    Defaults to Seedream-4.5 (251128) unless SEEDREAM4_MODEL is set.
    """
    return dotenv.get_dotenv_value("SEEDREAM4_MODEL", "seedream-4-5-251128")


SEEDREAM4_MODEL = get_model_name()


def is_enabled() -> bool:
    """Return True if Seedream4 integration is enabled via env flag."""
    enabled = (dotenv.get_dotenv_value("SEEDREAM4_ENABLED", "false") or "").lower()
    return enabled in ("1", "true", "yes", "on")


def get_api_key() -> str | None:
    """Return Seedream4 API key from environment, or None if missing."""
    return dotenv.get_dotenv_value("SEEDREAM4_API_KEY") or None


def build_headers(api_key: str) -> Dict[str, str]:
    """Build HTTP headers for calling the Seedream4 API."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
