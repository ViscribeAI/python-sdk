# Utility functions go here

import base64
from typing import Any, Dict
from urllib.parse import urlparse
from uuid import UUID

import aiohttp
from requests import Response

from viscribe.exceptions import APIError


def validate_api_key(api_key: str) -> bool:
    if not api_key.startswith("vscrb-"):
        raise ValueError("Invalid API key format. API key must start with 'vscrb-'")
    uuid_part = api_key[5:]  # Strip out 'vscrb-'
    try:
        UUID(uuid_part)
    except ValueError:
        raise ValueError(
            "Invalid API key format. API key must be 'vscrb-' followed by a valid UUID. You can get one at https://app.viscribe.ai/"
        )
    return True


def handle_sync_response(response: Response) -> Dict[str, Any]:
    data = response.json()

    if response.status_code >= 400:
        error_msg = data.get("error", "Unknown error occurred")
        raise APIError(error_msg, status_code=response.status_code)

    return data


async def handle_async_response(response: aiohttp.ClientResponse) -> Dict[str, Any]:
    data = await response.json()

    if response.status >= 400:
        error_msg = data.get("error", "Unknown error occurred")
        raise APIError(error_msg, status_code=response.status)

    return data


def validate_url_format(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("URL must have a valid scheme and netloc")
        if result.scheme not in ["http", "https"]:
            raise ValueError("URL scheme must be http or https")
        return True
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid URL format: {str(e)}")


def validate_base64_image(b64: str) -> bool:
    """Validate base64 encoded image format."""
    try:
        # Check if it's a data URL
        if b64.startswith("data:image/"):
            # Extract the base64 part after the comma
            b64_part = b64.split(",", 1)[1] if "," in b64 else b64
        else:
            b64_part = b64

        # Try to decode
        decoded = base64.b64decode(b64_part, validate=True)
        if len(decoded) == 0:
            raise ValueError("Base64 string is empty after decoding")
        return True
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid base64 image format: {str(e)}")
