import asyncio
from typing import Any, Optional

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError
from pydantic import BaseModel

from viscribe.config import API_BASE_URL, DEFAULT_HEADERS
from viscribe.exceptions import APIError
from viscribe.logger import viscribe_logger as logger
from viscribe.models.feedback import FeedbackRequest
from viscribe.utils.helpers import handle_async_response, validate_api_key
from viscribe.models.image import (
    ImageDescribeRequest, ImageDescribeResponse,
    ImageExtractRequest, ImageExtractResponse,
    ImageClassifyRequest, ImageClassifyResponse,
    ImageAskRequest, ImageAskResponse,
    ImageCompareRequest, ImageCompareResponse,
    CreditsResponse, FeedbackCreate, FeedbackResponse,
)


class AsyncClient:
    @classmethod
    def from_env(
        cls,
        verify_ssl: bool = True,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize AsyncClient using API key from environment variable.

        Args:
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds. None means no timeout (infinite)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        from os import getenv

        api_key = getenv("VISCRIBE_API_KEY")
        if not api_key:
            raise ValueError("VISCRIBE_API_KEY environment variable not set")
        return cls(
            api_key=api_key,
            verify_ssl=verify_ssl,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    def __init__(
        self,
        api_key: str = None,
        verify_ssl: bool = True,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize AsyncClient with configurable parameters.

        Args:
            api_key: API key for authentication. If None, will try to load from environment
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds. None means no timeout (infinite)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        logger.info("🔑 Initializing AsyncClient")

        # Try to get API key from environment if not provided
        if api_key is None:
            from os import getenv

            api_key = getenv("VISCRIBE_API_KEY")
            if not api_key:
                raise ValueError(
                    "VISCRIBE_API_KEY not provided and not found in environment"
                )

        validate_api_key(api_key)
        logger.debug(
            f"🛠️ Configuration: verify_ssl={verify_ssl}, timeout={timeout}, max_retries={max_retries}"
        )
        self.api_key = api_key
        self.headers = {**DEFAULT_HEADERS, "VISCRIBE-APIKEY": api_key}
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        ssl = None if verify_ssl else False
        self.timeout = ClientTimeout(total=timeout) if timeout is not None else None

        self.session = ClientSession(
            headers=self.headers, connector=TCPConnector(ssl=ssl), timeout=self.timeout
        )

        logger.info("✅ AsyncClient initialized successfully")

    async def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """Make HTTP request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"🚀 Making {method} request to {url} (Attempt {attempt + 1}/{self.max_retries})"
                )
                logger.debug(f"🔍 Request parameters: {kwargs}")

                async with self.session.request(method, url, **kwargs) as response:
                    logger.debug(f"📥 Response status: {response.status}")
                    result = await handle_async_response(response)
                    logger.info(f"✅ Request completed successfully: {method} {url}")
                    return result

            except ClientError as e:
                logger.warning(f"⚠️ Request attempt {attempt + 1} failed: {str(e)}")
                if hasattr(e, "status") and e.status is not None:
                    try:
                        error_data = await e.response.json()
                        error_msg = error_data.get("error", str(e))
                        logger.error(f"🔴 API Error: {error_msg}")
                        raise APIError(error_msg, status_code=e.status)
                    except ValueError:
                        logger.error("🔴 Could not parse error response")
                        raise APIError(
                            str(e),
                            status_code=e.status if hasattr(e, "status") else None,
                        )

                if attempt == self.max_retries - 1:
                    logger.error(f"❌ All retry attempts failed for {method} {url}")
                    raise ConnectionError(f"Failed to connect to API: {str(e)}")

                retry_delay = self.retry_delay * (attempt + 1)
                logger.info(f"⏳ Waiting {retry_delay}s before retry {attempt + 2}")
                await asyncio.sleep(retry_delay)

    async def submit_feedback(
        self, request_id: str, rating: int, feedback_text: Optional[str] = None
    ):
        """Submit feedback for a request"""
        logger.info(f"📝 Submitting feedback for request {request_id}")
        logger.debug(f"⭐ Rating: {rating}, Feedback: {feedback_text}")

        feedback = FeedbackRequest(
            request_id=request_id, rating=rating, feedback_text=feedback_text
        )
        logger.debug("✅ Feedback validation passed")

        result = await self._make_request(
            "POST", f"{API_BASE_URL}/feedback", json=feedback.model_dump()
        )
        logger.info("✨ Feedback submitted successfully")
        return result

    async def get_credits(self):
        """Get credits information"""
        logger.info("💳 Fetching credits information")

        result = await self._make_request(
            "GET",
            f"{API_BASE_URL}/credits",
        )
        logger.info(
            f"✨ Credits info retrieved: {result.get('remaining_credits')} credits remaining"
        )
        return result

    async def close(self):
        """Close the session to free up resources"""
        logger.info("🔒 Closing AsyncClient session")
        await self.session.close()
        logger.debug("✅ Session closed successfully")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def describe_image(self, request: ImageDescribeRequest) -> ImageDescribeResponse:
        """Send a describe image request"""
        logger.info("🔍 Starting image describe request")
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/describe", json=request.model_dump()
        )
        return ImageDescribeResponse(**result)

    async def extract_image(self, request: ImageExtractRequest) -> ImageExtractResponse:
        """Send an extract structured data from image request"""
        logger.info("🔍 Starting image extract request")
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/extract", json=request.model_dump()
        )
        return ImageExtractResponse(**result)

    async def classify_image(self, request: ImageClassifyRequest) -> ImageClassifyResponse:
        """Send an image classify request"""
        logger.info("🔍 Starting image classify request")
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/classify", json=request.model_dump()
        )
        return ImageClassifyResponse(**result)

    async def ask_image(self, request: ImageAskRequest) -> ImageAskResponse:
        """Send an image VQA (ask) request"""
        logger.info("🔍 Starting image ask (VQA) request")
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/ask", json=request.model_dump()
        )
        return ImageAskResponse(**result)

    async def compare_images(self, request: ImageCompareRequest) -> ImageCompareResponse:
        """Send an image compare request"""
        logger.info("🔍 Starting image compare request")
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/compare", json=request.model_dump()
        )
        return ImageCompareResponse(**result)

    async def get_credits(self) -> CreditsResponse:
        """Get credits information"""
        logger.info("💳 Fetching credits information")
        result = await self._make_request("GET", f"{API_BASE_URL}/credits")
        return CreditsResponse(**result)

    async def submit_feedback(self, request: FeedbackCreate) -> FeedbackResponse:
        """Submit feedback for a request"""
        logger.info(f"📝 Submitting feedback for request {request.request_id}")
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/feedback", json=request.model_dump()
        )
        return FeedbackResponse(**result)
