from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def notify_hope(callback_url: str, payload: dict) -> bool:
    """Notify HOPE that an analysis run has completed."""
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
