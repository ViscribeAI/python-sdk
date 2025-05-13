from uuid import uuid4
import base64

import pytest
import responses

from viscribe.client import Client
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


@responses.activate
def test_get_credits(mock_api_key):
    responses.add(
        responses.GET,
        "https://api.ViscribeAI.com/v1/credits",
        json={"remaining_credits": 100, "total_credits_used": 50},
    )

    with Client(api_key=mock_api_key) as client:
        response = client.get_credits()
        assert response["remaining_credits"] == 100
        assert response["total_credits_used"] == 50


@responses.activate
def test_submit_feedback(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.ViscribeAI.com/v1/feedback",
        json={"status": "success"},
    )

    with Client(api_key=mock_api_key) as client:
        response = client.submit_feedback(
            request_id=str(uuid4()), rating=5, feedback_text="Great service!"
        )
        assert response["status"] == "success"


@responses.activate
def test_network_error(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.viscribe.ai/v1/images/describe",
        body=ConnectionError("Network error"),
    )

    with Client(api_key=mock_api_key) as client:
        with pytest.raises(ConnectionError):
            client.describe_image(
                image_url="https://example.com"
            )


def test_describe_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.ViscribeAI.com/v1/images/describe",
        json={
            "request_id": "req-1",
            "credits_used": 1,
            "image_description": "A cat on a mat.",
            "tags": ["cat", "mat"]
        },
    )
    req = ImageDescribeRequest(image_url="https://img.com/cat.jpg")
    with Client(api_key=mock_api_key) as client:
        resp = client.describe_image(req)
        assert resp.request_id == "req-1"
        assert resp.image_description == "A cat on a mat."
        assert resp.tags == ["cat", "mat"]


def test_extract_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.ViscribeAI.com/v1/images/extract",
        json={
            "request_id": "req-2",
            "credits_used": 2,
            "extracted_data": {"product_name": "Widget", "price": 9.99}
        },
    )
    req = ImageExtractRequest(image_url="https://img.com/prod.jpg", output_schema={"type": "object"})
    with Client(api_key=mock_api_key) as client:
        resp = client.extract_image(req)
        assert resp.request_id == "req-2"
        assert resp.extracted_data["product_name"] == "Widget"
        assert resp.extracted_data["price"] == 9.99


def test_classify_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.ViscribeAI.com/v1/images/classify",
        json={
            "request_id": "req-3",
            "credits_used": 1,
            "classification": ["cat"]
        },
    )
    req = ImageClassifyRequest(image_url="https://img.com/cat.jpg", classes=["cat", "dog"])
    with Client(api_key=mock_api_key) as client:
        resp = client.classify_image(req)
        assert resp.request_id == "req-3"
        assert resp.classification == ["cat"]


def test_ask_image(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.ViscribeAI.com/v1/images/ask",
        json={
            "request_id": "req-4",
            "credits_used": 1,
            "answer": "Blue"
        },
    )
    req = ImageAskRequest(image_url="https://img.com/car.jpg", question="What color is the car?")
    with Client(api_key=mock_api_key) as client:
        resp = client.ask_image(req)
        assert resp.request_id == "req-4"
        assert resp.answer == "Blue"


def test_compare_images(mock_api_key):
    responses.add(
        responses.POST,
        "https://api.ViscribeAI.com/v1/images/compare",
        json={
            "request_id": "req-5",
            "credits_used": 2,
            "comparison_result": "Both images show cats, but one is black and one is white."
        },
    )
    req = ImageCompareRequest(image1_url="https://img.com/cat1.jpg", image2_url="https://img.com/cat2.jpg")
    with Client(api_key=mock_api_key) as client:
        resp = client.compare_images(req)
        assert resp.request_id == "req-5"
        assert "cats" in resp.comparison_result
