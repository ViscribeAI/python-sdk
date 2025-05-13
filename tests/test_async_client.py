from uuid import uuid4
import base64

import pytest
from aioresponses import aioresponses

from viscribe.async_client import AsyncClient
from viscribe.exceptions import APIError
from tests.utils import generate_mock_api_key
from viscribe.models.image import (
    ImageDescribeRequest, ImageDescribeResponse,
    ImageExtractRequest, ImageExtractResponse,
    ImageClassifyRequest, ImageClassifyResponse,
    ImageAskRequest, ImageAskResponse,
    ImageCompareRequest, ImageCompareResponse,
)


@pytest.fixture
def mock_api_key():
    return generate_mock_api_key()


@pytest.fixture
def mock_uuid():
    return str(uuid4())

@pytest.mark.asyncio
async def test_get_credits(mock_api_key):
    with aioresponses() as mocked:
        mocked.get(
            "https://api.ViscribeAI.com/v1/credits",
            payload={"remaining_credits": 100, "total_credits_used": 50},
        )

        async with AsyncClient(api_key=mock_api_key) as client:
            response = await client.get_credits()
            assert response["remaining_credits"] == 100
            assert response["total_credits_used"] == 50


@pytest.mark.asyncio
async def test_submit_feedback(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.ViscribeAI.com/v1/feedback", payload={"status": "success"}
        )

        async with AsyncClient(api_key=mock_api_key) as client:
            response = await client.submit_feedback(
                request_id=str(uuid4()), rating=5, feedback_text="Great service!"
            )
            assert response["status"] == "success"



@pytest.mark.asyncio
async def test_api_error(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.viscribe.ai/v1/images/describe",
            status=400,
            payload={"error": "Bad request"},
            exception=APIError("Bad request", status_code=400),
        )

        async with AsyncClient(api_key=mock_api_key) as client:
            with pytest.raises(APIError) as exc_info:
                await client.describe_image(
                    image_url="https://example.com"
                )
            assert exc_info.value.status_code == 400
            assert "Bad request" in str(exc_info.value)

@pytest.mark.asyncio
async def test_describe_image(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.ViscribeAI.com/v1/images/describe",
            payload={
                "request_id": "req-1",
                "credits_used": 1,
                "image_description": "A cat on a mat.",
                "tags": ["cat", "mat"]
            },
        )
        req = ImageDescribeRequest(image_url="https://img.com/cat.jpg")
        async with AsyncClient(api_key=mock_api_key) as client:
            resp = await client.describe_image(req)
            assert resp.request_id == "req-1"
            assert resp.image_description == "A cat on a mat."
            assert resp.tags == ["cat", "mat"]


@pytest.mark.asyncio
async def test_extract_image(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.ViscribeAI.com/v1/images/extract",
            payload={
                "request_id": "req-2",
                "credits_used": 2,
                "extracted_data": {"product_name": "Widget", "price": 9.99}
            },
        )
        req = ImageExtractRequest(image_url="https://img.com/prod.jpg", output_schema={"type": "object"})
        async with AsyncClient(api_key=mock_api_key) as client:
            resp = await client.extract_image(req)
            assert resp.request_id == "req-2"
            assert resp.extracted_data["product_name"] == "Widget"
            assert resp.extracted_data["price"] == 9.99


@pytest.mark.asyncio
async def test_classify_image(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.ViscribeAI.com/v1/images/classify",
            payload={
                "request_id": "req-3",
                "credits_used": 1,
                "classification": ["cat"]
            },
        )
        req = ImageClassifyRequest(image_url="https://img.com/cat.jpg", classes=["cat", "dog"])
        async with AsyncClient(api_key=mock_api_key) as client:
            resp = await client.classify_image(req)
            assert resp.request_id == "req-3"
            assert resp.classification == ["cat"]


@pytest.mark.asyncio
async def test_ask_image(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.ViscribeAI.com/v1/images/ask",
            payload={
                "request_id": "req-4",
                "credits_used": 1,
                "answer": "Blue"
            },
        )
        req = ImageAskRequest(image_url="https://img.com/car.jpg", question="What color is the car?")
        async with AsyncClient(api_key=mock_api_key) as client:
            resp = await client.ask_image(req)
            assert resp.request_id == "req-4"
            assert resp.answer == "Blue"


@pytest.mark.asyncio
async def test_compare_images(mock_api_key):
    with aioresponses() as mocked:
        mocked.post(
            "https://api.ViscribeAI.com/v1/images/compare",
            payload={
                "request_id": "req-5",
                "credits_used": 2,
                "comparison_result": "Both images show cats, but one is black and one is white."
            },
        )
        req = ImageCompareRequest(image1_url="https://img.com/cat1.jpg", image2_url="https://img.com/cat2.jpg")
        async with AsyncClient(api_key=mock_api_key) as client:
            resp = await client.compare_images(req)
            assert resp.request_id == "req-5"
            assert "cats" in resp.comparison_result
