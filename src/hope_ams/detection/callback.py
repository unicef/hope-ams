import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def notify_hope(callback_url: str, payload: dict[str, Any]) -> bool:
    """Notify HOPE that an analysis run has completed.

    Only allowed to POST to URLs under HOPE_API_URL (SSRF guard).
    """
    allowed_base = getattr(settings, "HOPE_API_URL", "")
    if not callback_url or not allowed_base or not callback_url.startswith(allowed_base.rstrip("/")):
        logger.warning("Callback URL %s not allowed (must start with %s)", callback_url, allowed_base)
        return False
    try:
        timeout = getattr(settings, "AMS_CALLBACK_TIMEOUT", 10)
        resp = requests.post(
            callback_url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        logger.info("Callback to %s succeeded (status=%s)", callback_url, resp.status_code)
    except requests.RequestException as e:
        logger.warning("Callback to %s failed: %s", callback_url, e)
        return False
    else:
        return True
