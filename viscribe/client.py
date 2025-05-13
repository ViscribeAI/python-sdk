# Client implementation goes here
from typing import Any, Optional

import requests
import urllib3
from requests.exceptions import RequestException

from viscribe.config import API_BASE_URL, DEFAULT_HEADERS
from viscribe.exceptions import APIError
from viscribe.logger import viscribe_logger as logger
from viscribe.models.image import CreditsResponse, FeedbackCreate, FeedbackResponse
from viscribe.utils.helpers import handle_sync_response, validate_api_key


class Client:
    @classmethod
    def from_env(
        cls,
        verify_ssl: bool = True,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize Client using API key from environment variable.

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
        """Initialize Client with configurable parameters.

        Args:
            api_key: API key for authentication. If None, will try to load from environment
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds. None means no timeout (infinite)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        logger.info("🔑 Initializing Client")

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
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Create a session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = verify_ssl

        # Configure retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.urllib3.Retry(
                total=max_retries,
                backoff_factor=retry_delay,
                status_forcelist=[500, 502, 503, 504],
            )
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Add warning suppression if verify_ssl is False
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        logger.info("✅ Client initialized successfully")

    def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """Make HTTP request with error handling."""
        try:
            logger.info(f"🚀 Making {method} request to {url}")
            logger.debug(f"🔍 Request parameters: {kwargs}")

            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            logger.debug(f"📥 Response status: {response.status_code}")

            result = handle_sync_response(response)
            logger.info(f"✅ Request completed successfully: {method} {url}")
            return result

        except RequestException as e:
            logger.error(f"❌ Request failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", str(e))
                    logger.error(f"🔴 API Error: {error_msg}")
                    raise APIError(error_msg, status_code=e.response.status_code)
                except ValueError:
                    logger.error("🔴 Could not parse error response")
                    raise APIError(
                        str(e),
                        status_code=(
                            e.response.status_code
                            if hasattr(e.response, "status_code")
                            else None
                        ),
                    )
            logger.error(f"🔴 Connection Error: {str(e)}")
            raise ConnectionError(f"Failed to connect to API: {str(e)}")

    def submit_feedback(self, request: FeedbackCreate) -> FeedbackResponse:
        """Submit feedback for a request"""
        logger.info(f"📝 Submitting feedback for request {request.request_id}")
        result = self._make_request(
            "POST", f"{API_BASE_URL}/feedback", json=request.model_dump()
        )
        return FeedbackResponse(**result)

    def get_credits(self) -> CreditsResponse:
        """Get credits information"""
        logger.info("💳 Fetching credits information")
        result = self._make_request("GET", f"{API_BASE_URL}/credits")
        return CreditsResponse(**result)

    def describe_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        instruction: str = None,
        generate_tags: bool = True,
    ):
        """Send a describe image request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image describe request")
        from viscribe.models.image import ImageDescribeRequest, ImageDescribeResponse

        req = ImageDescribeRequest(
            image_url=image_url,
            image_base64=image_base64,
            instruction=instruction,
            generate_tags=generate_tags,
        )
        payload = req.model_dump(exclude_none=True)
        result = self._make_request(
            "POST", f"{API_BASE_URL}/images/describe", json=payload
        )
        return ImageDescribeResponse(**result)

    def extract_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        output_schema: dict = None,
        instruction: str = None,
    ):
        """Send an extract structured data from image request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image extract request")
        from viscribe.models.image import ImageExtractRequest, ImageExtractResponse

        req = ImageExtractRequest(
            image_url=image_url,
            image_base64=image_base64,
            output_schema=output_schema,
            instruction=instruction,
        )
        payload = req.model_dump(exclude_none=True)
        result = self._make_request(
            "POST", f"{API_BASE_URL}/images/extract", json=payload
        )
        return ImageExtractResponse(**result)

    def classify_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        classes: list = None,
        class_descriptions: dict = None,
        instruction: str = None,
        multi_label: bool = False,
    ):
        """Send an image classify request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image classify request")
        from viscribe.models.image import ImageClassifyRequest, ImageClassifyResponse

        req = ImageClassifyRequest(
            image_url=image_url,
            image_base64=image_base64,
            classes=classes,
            class_descriptions=class_descriptions,
            instruction=instruction,
            multi_label=multi_label,
        )
        payload = req.model_dump(exclude_none=True)
        result = self._make_request(
            "POST", f"{API_BASE_URL}/images/classify", json=payload
        )
        return ImageClassifyResponse(**result)

    def ask_image(
        self,
        image_url: str = None,
        image_base64: str = None,
        question: str = None,
    ):
        """Send an image VQA (ask) request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image ask (VQA) request")
        from viscribe.models.image import ImageAskRequest, ImageAskResponse

        req = ImageAskRequest(
            image_url=image_url,
            image_base64=image_base64,
            question=question,
        )
        payload = req.model_dump(exclude_none=True)
        result = self._make_request("POST", f"{API_BASE_URL}/images/ask", json=payload)
        return ImageAskResponse(**result)

    def compare_images(
        self,
        image1_url: str = None,
        image1_base64: str = None,
        image2_url: str = None,
        image2_base64: str = None,
        instruction: str = None,
    ):
        """Send an image compare request with explicit arguments and validate with Pydantic."""
        logger.info("🔍 Starting image compare request")
        from viscribe.models.image import ImageCompareRequest, ImageCompareResponse

        req = ImageCompareRequest(
            image1_url=image1_url,
            image1_base64=image1_base64,
            image2_url=image2_url,
            image2_base64=image2_base64,
            instruction=instruction,
        )
        payload = req.model_dump(exclude_none=True)
        result = self._make_request(
            "POST", f"{API_BASE_URL}/images/compare", json=payload
        )
        return ImageCompareResponse(**result)

    def close(self):
        """Close the session to free up resources"""
        logger.info("🔒 Closing Client session")
        self.session.close()
        logger.debug("✅ Session closed successfully")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
