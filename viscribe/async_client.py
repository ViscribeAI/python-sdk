import asyncio
from typing import Any, Optional, Type, Union

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError
from pydantic import BaseModel

from viscribe.config import API_BASE_URL, DEFAULT_HEADERS
from viscribe.exceptions import APIError
from viscribe.logger import viscribe_logger as logger
from viscribe.models.image import (
    CreditsResponse,
    ExtractField,
    FeedbackRequest,
    FeedbackResponse,
    ImageAskRequest,
    ImageAskResponse,
    ImageClassifyRequest,
    ImageClassifyResponse,
    ImageCompareRequest,
    ImageCompareResponse,
    ImageDescribeRequest,
    ImageDescribeResponse,
    ImageExtractRequest,
    ImageExtractResponse,
)
from viscribe.utils.helpers import handle_async_response, validate_api_key


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

    async def submit_feedback(self, request_id: str, rating: int, feedback_text: Optional[str] = None) -> FeedbackResponse:
        """Submit feedback for a request"""
        logger.info(f"📝 Submitting feedback for request {request_id}")
        feedback = FeedbackRequest(
            request_id=request_id, rating=rating, feedback_text=feedback_text
        )
        payload = feedback.model_dump(exclude_none=True)
        result = await self._make_request("POST", f"{API_BASE_URL}/feedback", json=payload)
        return FeedbackResponse(**result)

    async def get_credits(self) -> CreditsResponse:
        """Get credits information"""
        logger.info("💳 Fetching credits information")
        result = await self._make_request("GET", f"{API_BASE_URL}/credits")
        return CreditsResponse(**result)

    async def close(self):
        """Close the session to free up resources"""
        logger.info("🔒 Closing AsyncClient session")
        await self.session.close()
        logger.debug("✅ Session closed successfully")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def describe_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        instruction: str = None,
        generate_tags: bool = True,
    ) -> ImageDescribeResponse:
        """Send a describe image request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image describe request")

        req = ImageDescribeRequest(
            image_url=image_url,
            image_base64=image_base64,
            instruction=instruction,
            generate_tags=generate_tags,
        )
        payload = req.model_dump(exclude_none=True)
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/describe", json=payload
        )
        return ImageDescribeResponse(**result)

    async def extract_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        fields: list = None,
        advanced_schema: Union[dict, BaseModel, Type[BaseModel]] = None,
        instruction: str = None,
    ) -> ImageExtractResponse:
        """Send an extract structured data from image request with explicit arguments and validate with Pydantic.
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded string of the image
            fields: List of dictionaries with 'name', 'type', and optional 'description' keys.
                   Each field type can be 'text', 'number', 'array_text' (max 5), or 'array_number' (max 5).
                   Max 10 fields allowed.
            advanced_schema: Full JSON schema for complex extraction (dict), a Pydantic BaseModel instance,
                           or a Pydantic BaseModel class. If a BaseModel is provided, it will be serialized
                           to its JSON schema. Use this for nested structures.
            instruction: Optional instruction to guide the extraction process.
        
        Note: Either fields or advanced_schema must be provided, not both.
        """
        logger.info("🔍 Starting image extract request")

        # Convert dictionaries to ExtractField models if fields are provided
        validated_fields = None
        if fields is not None:
            validated_fields = [ExtractField(**field) if isinstance(field, dict) else field for field in fields]

        # Convert Pydantic BaseModel to JSON schema if advanced_schema is a BaseModel
        validated_schema = advanced_schema
        if advanced_schema is not None:
            if isinstance(advanced_schema, BaseModel):
                # BaseModel instance
                validated_schema = advanced_schema.model_json_schema()
            elif isinstance(advanced_schema, type) and issubclass(advanced_schema, BaseModel):
                # BaseModel class
                validated_schema = advanced_schema.model_json_schema()

        req = ImageExtractRequest(
            image_url=image_url,
            image_base64=image_base64,
            fields=validated_fields,
            advanced_schema=validated_schema,
            instruction=instruction,
        )
        payload = req.model_dump(exclude_none=True)
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/extract", json=payload
        )
        return ImageExtractResponse(**result)

    async def classify_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        classes: list = None,
        class_descriptions: dict = None,
        instruction: str = None,
        multi_label: bool = False,
    ) -> ImageClassifyResponse:
        """Send an image classify request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image classify request")

        req = ImageClassifyRequest(
            image_url=image_url,
            image_base64=image_base64,
            classes=classes,
            class_descriptions=class_descriptions,
            instruction=instruction,
            multi_label=multi_label,
        )
        payload = req.model_dump(exclude_none=True)
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/classify", json=payload
        )
        return ImageClassifyResponse(**result)

    async def ask_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        question: str = None,
    ) -> ImageAskResponse:
        """Send an image VQA (ask) request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image ask (VQA) request")

        req = ImageAskRequest(
            image_url=image_url,
            image_base64=image_base64,
            question=question,
        )
        payload = req.model_dump(exclude_none=True)
        result = await self._make_request("POST", f"{API_BASE_URL}/images/ask", json=payload)
        return ImageAskResponse(**result)

    async def compare_images(
        self,
        image1_url: str = None,
        image1_base64: str = None,
        image2_url: str = None,
        image2_base64: str = None,
        instruction: str = None,
    ) -> ImageCompareResponse:
        """Send an image compare request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image compare request")

        req = ImageCompareRequest(
            image1_url=image1_url,
            image1_base64=image1_base64,
            image2_url=image2_url,
            image2_base64=image2_base64,
            instruction=instruction,
        )
        payload = req.model_dump(exclude_none=True)
        result = await self._make_request(
            "POST", f"{API_BASE_URL}/images/compare", json=payload
        )
        return ImageCompareResponse(**result)


